"""La chiave di traduzione si dichiara, e dichiararla non muove l'entity_id.

Perche' questo test esiste. Fino al 27 settembre 2026 `Omoda9Entity` RICAVAVA la chiave
di traduzione dall'`object_id`, cioe' dallo stesso nome italiano da cui si costruisce
l'entity_id: chiave ed entity_id erano la stessa stringa scritta una volta sola. La
conseguenza non stava scritta da nessuna parte e ha diretto la pianificazione per tre
settimane: portare le chiavi in inglese sembrava richiedere di muovere ogni entity_id, e
quindi sembrava potersi fare SOLO nella release del cambio di dominio, l'unico momento in
cui gli entity_id si rigenerano comunque.

Non era un vincolo di Home Assistant: era una riga. Questi due test fissano la
separazione, perche' e' il genere di accoppiamento che si riforma da solo alla prossima
rifattorizzazione - e se si riforma, il piano di migrazione torna sbagliato senza che
nulla lo segnali.
"""
from __future__ import annotations


def _coord(hass, entry):
    from custom_components.omoda9.const import DOMAIN
    return hass.data[DOMAIN][entry.entry_id]


def test_chiave_dichiarata_vince_sulla_derivazione(hass, integrazione_avviata):
    """Passando `translation_key` la chiave e' quella, e l'entity_id resta quello di prima."""
    from custom_components.omoda9.entity import Omoda9Entity

    coord = _coord(hass, integrazione_avviata)

    derivata = Omoda9Entity(coord, "Batteria", "batteria_x1")
    assert derivata.translation_key == "batteria", "la derivazione storica deve restare il ripiego"

    dichiarata = Omoda9Entity(coord, "Batteria", "batteria_x2", translation_key="battery")
    assert dichiarata.translation_key == "battery"

    # Il punto di tutta la modifica: la chiave e' cambiata, l'identita' no.
    assert dichiarata._raw_name == derivata._raw_name
    assert dichiarata.unique_id != derivata.unique_id      # suffissi diversi, di proposito
    assert dichiarata.unique_id.endswith("batteria_x2")
    # `unique_id` non contiene il dominio: e' cio' che rende il rename delle chiavi
    # indipendente dal rename del dominio.
    from custom_components.omoda9.const import DOMAIN
    assert DOMAIN not in dichiarata.unique_id


def test_entity_id_esplicito_non_dipende_dalla_chiave(hass, integrazione_avviata):
    """Con `object_id` + `entity_id_format`, l'entity_id e' scritto a mano: una chiave
    inglese non lo tocca. E' la forma che useranno le 110 entita' quando verranno
    convertite, ed e' la ragione per cui la conversione non rompe nessuna installazione."""
    from custom_components.omoda9.entity import Omoda9Entity

    coord = _coord(hass, integrazione_avviata)
    fmt = "sensor.{}"

    it = Omoda9Entity(coord, "Batteria scarica", "bs1",
                      object_id="omoda9_batteria_scarica", entity_id_format=fmt)
    en = Omoda9Entity(coord, "Batteria scarica", "bs2",
                      object_id="omoda9_batteria_scarica", entity_id_format=fmt,
                      translation_key="battery_low")

    assert it.entity_id == en.entity_id == "sensor.omoda9_batteria_scarica"
    assert it.translation_key == "batteria_scarica"
    assert en.translation_key == "battery_low"
