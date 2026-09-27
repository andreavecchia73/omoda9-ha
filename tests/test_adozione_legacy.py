"""Adozione delle entita' della linea `omoda_jaecoo`, con il loro storico.

Chi viene dalla linea del fork non sta aggiornando: per Home Assistant quella e' un'altra
integrazione. Senza adozione si ritrova 110 entita' nuove e vuote mentre le sue, con anni
di storico, restano attaccate a un'integrazione che sta per disinstallare. Lo storico non
si esporta: o viene adottato adesso, o e' perso.

Il meccanismo e' `async_update_entity_platform`, che Home Assistant documenta esattamente
per questo e che NESSUNA delle sue 1401 integrazioni usa. Quindi ogni proprieta' e' fissata
qui: non e' un percorso su cui ci si possa appoggiare all'esperienza di altri.
"""
from __future__ import annotations

import pytest

VIN = "VINFINTO"


@pytest.fixture
def registro(hass):
    from homeassistant.helpers import entity_registry as er
    return er.async_get(hass)


def _vecchia(registro, config_entry_legacy, piattaforma, suffisso, object_id):
    return registro.async_get_or_create(
        piattaforma, "omoda_jaecoo", f"{VIN}_{suffisso}",
        suggested_object_id=object_id, config_entry=config_entry_legacy)


@pytest.fixture
def config_entry_legacy(hass):
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    e = MockConfigEntry(domain="omoda_jaecoo", data={}, title="vecchia")
    e.add_to_hass(hass)
    return e


@pytest.fixture
def entry_nostro(hass, config_entry):
    hass.config_entries.async_update_entry(config_entry, data={**config_entry.data, "vin": VIN})
    return config_entry


async def test_un_suffisso_identico_viene_adottato(hass, registro, entry_nostro, config_entry_legacy):
    """Il caso degli 83: il suffisso e' il nome del campo dell'API Chery, uguale sulle due
    linee. L'entita' cambia integrazione e nome, e resta la stessa entita' - che e' il punto,
    perche' e' l'identita' a cui lo storico e' attaccato."""
    from custom_components.omoda9.legacy import adotta
    from custom_components.omoda9.const import DOMAIN

    _vecchia(registro, config_entry_legacy, "binary_sensor", "engineState", "engine")

    r = adotta(hass, entry_nostro)

    assert len(r["adottate"]) == 1
    nuova = registro.async_get("binary_sensor.chery_connect_engine")
    assert nuova is not None, "l'entita' non e' stata rinominata"
    assert nuova.platform == DOMAIN, "l'entita' non e' passata alla nostra integrazione"
    assert nuova.unique_id == f"{VIN}_engineState"


async def test_un_suffisso_diverso_usa_la_tabella(hass, registro, entry_nostro, config_entry_legacy):
    """Il caso dei 13: stessa entita', suffisso scritto nella lingua di chi l'ha aggiunta.
    Senza la tabella queste resterebbero orfane, e sono quelle che l'utente nota."""
    from custom_components.omoda9.legacy import adotta

    _vecchia(registro, config_entry_legacy, "binary_sensor", "rt_battery_low", "battery_low")

    r = adotta(hass, entry_nostro)

    assert len(r["adottate"]) == 1
    nuova = registro.async_get("binary_sensor.chery_connect_low_battery")
    assert nuova is not None
    assert nuova.unique_id == f"{VIN}_rt_batteria_scarica"


async def test_la_gemella_vuota_lascia_il_posto_a_quella_con_lo_storico(
        hass, registro, entry_nostro, config_entry_legacy):
    """Chi configura l'integrazione PRIMA di adottare si ritrova due entita' per la stessa
    cosa: la nostra, nuova e vuota, e la sua, piena. Vince quella piena.

    E' l'unico punto in cui questa funzione cancella qualcosa. Cancella solo roba nostra, e
    solo quando ha il rimpiazzo gia' in mano."""
    from custom_components.omoda9.legacy import adotta

    registro.async_get_or_create(
        "binary_sensor", "omoda9", f"{VIN}_engineState",
        suggested_object_id="chery_connect_engine", config_entry=entry_nostro)
    _vecchia(registro, config_entry_legacy, "binary_sensor", "engineState", "engine")

    r = adotta(hass, entry_nostro)

    assert r["sostituite"] == 1
    nuova = registro.async_get("binary_sensor.chery_connect_engine")
    assert nuova.unique_id == f"{VIN}_engineState"
    # una sola entita' per quella cosa, non due
    tutte = [e for e in registro.entities.values() if e.unique_id == f"{VIN}_engineState"]
    assert len(tutte) == 1


async def test_cio_che_non_si_puo_adottare_viene_dichiarato(hass, registro, entry_nostro, config_entry_legacy):
    """Cinque entita' non sono portabili: due perche' le due linee le hanno fatte di tipo
    diverso, tre perche' sul canonico non esistono. Devono comparire nel rapporto: un numero
    che non torna, scoperto dall'utente dopo, costa la fiducia in tutto il resto."""
    from custom_components.omoda9.legacy import adotta

    _vecchia(registro, config_entry_legacy, "select", "windows_select", "windows")

    r = adotta(hass, entry_nostro)

    assert not r["adottate"]
    assert len(r["non_migrabili"]) == 1
    assert "select" in r["non_migrabili"][0][1] or "cover" in r["non_migrabili"][0][1]
    assert registro.async_get("select.windows") is not None


async def test_dry_run_non_scrive_niente(hass, registro, entry_nostro, config_entry_legacy):
    """Far vedere cosa succederebbe, prima che succeda. Su un'operazione senza precedenti
    in 1401 integrazioni, e' il minimo."""
    from custom_components.omoda9.legacy import adotta

    v = _vecchia(registro, config_entry_legacy, "binary_sensor", "engineState", "engine")

    r = adotta(hass, entry_nostro, dry_run=True)

    assert len(r["adottate"]) == 1
    ancora = registro.async_get(v.entity_id)
    assert ancora is not None and ancora.platform == "omoda_jaecoo", \
        "il dry run ha scritto sul registro"


async def test_le_entita_di_un_altro_veicolo_non_si_toccano(hass, registro, entry_nostro, config_entry_legacy):
    """Due auto sullo stesso Home Assistant: adottare quelle dell'altra sarebbe peggio che
    non adottare niente."""
    from custom_components.omoda9.legacy import adotta

    registro.async_get_or_create(
        "binary_sensor", "omoda_jaecoo", "UNALTROVIN_engineState",
        suggested_object_id="altra_engine", config_entry=config_entry_legacy)

    r = adotta(hass, entry_nostro)

    assert not r["adottate"]
    assert len(r["saltate"]) == 1


async def test_il_servizio_rifiuta_se_la_vecchia_e_ancora_accesa(
        hass, registro, integrazione_avviata, config_entry_legacy):
    """Home Assistant rifiuta di spostare un'entita' gia' montata: "Only entities that
    haven't been loaded can be migrated". Se non lo si dice prima, l'utente vede
    centouno fallimenti di fila e non capisce perche'."""
    from homeassistant.config_entries import ConfigEntryState
    from homeassistant.exceptions import HomeAssistantError
    import pytest as _pytest

    from custom_components.omoda9.const import DOMAIN

    _vecchia(registro, config_entry_legacy, "binary_sensor", "engineState", "engine")
    config_entry_legacy.mock_state(hass, ConfigEntryState.LOADED)

    assert hass.services.has_service(DOMAIN, "adopt_legacy_entities"), \
        "il servizio non e' registrato"
    with _pytest.raises(HomeAssistantError, match="ancora attiva"):
        await hass.services.async_call(
            DOMAIN, "adopt_legacy_entities", {"dry_run": True}, blocking=True)

    # e non ha toccato niente
    assert registro.async_get("binary_sensor.engine").platform == "omoda_jaecoo"
