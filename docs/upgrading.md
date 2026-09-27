# What you have to do, depending on where you are coming from

Two different situations, and they are not the same amount of work. Find yours.

## You already have this integration (domain `omoda9`)

**Three steps, and the third one is optional.**

1. Update in HACS.
2. Restart Home Assistant.
3. Read the notice that appears in Settings and fix your own automations.

That is the whole procedure. **Do not uninstall anything**, do not remove the
integration, do not log in again. The folder, the config entry and the mutual-TLS
certificates all stay where they are.

**What happens on that restart.** Every entity is renamed from its Italian id to
an English one: `sensor.omoda9_batteria` becomes
`sensor.chery_connect_battery`. The integration does it itself, before anything
is loaded.

**Your history comes with it.** Home Assistant moves long-term statistics and
state history when an entity is renamed through the registry. Graphs, the energy
dashboard and the logbook follow. Nothing to export, nothing to rebuild.

**What does not come with it: anything you typed yourself.** An automation,
script, template sensor or dashboard card that names an entity in text still
points at a name that no longer exists. Home Assistant shows those as unknown
entities.

**How to find yours** - this is the part people get stuck on, so it is answered
rather than left as an exercise:

- a notice appears in **Settings -> Devices & services -> Repairs**, saying how
  many entities were renamed on your vehicle;
- **Settings -> Automations & scenes**: an automation referring to a missing
  entity is flagged there;
- **Settings -> Dashboards**: a card pointing at nothing renders as an error;
- the complete old-to-new list is in [`entity-id-rename.md`](entity-id-rename.md).
  If you keep your automations in YAML, one search and replace per line does it.

Dismiss the notice when you are through. It will not come back.

## You are coming from the `omoda_jaecoo` line (JackRonan's fork)

**This is a fresh installation, and it is honest to say so up front: your history
does not come across.**

That line is a different integration as far as Home Assistant is concerned - a
different domain, a different folder, a different set of entities. Nothing can
be migrated between the two automatically, and the one Home Assistant API that
moves entities between integrations is used by none of the 1,401 integrations
shipped with it. We are not putting your car on that path.

**What you get instead:** you set up once, on the final English names, and never
repeat it. That is why the timing matters.

**Do it after this release, not before.** If you migrate first and this rename
lands afterwards, you rebuild your automations twice: once against the Italian
names, once against the English ones.

**The steps:**

1. Install this integration from HACS. It lands beside your existing one, in its
   own folder. Nothing of yours is touched yet.
2. Add it in **Settings -> Devices & services -> Add integration**. You will log
   in from scratch: this is a different integration and it has no session.
3. **When the form asks for `certs_src`, give it the path of your old
   certificate folder** - `config/omoda_jaecoo_<VIN>_certs`. The integration
   copies the certificates across itself. Do not move files by hand.
4. Check that your car appears and that the entities have values.
5. Rebuild the automations and dashboards you care about, against the new
   entity names.
6. **Only then** remove the old integration, and delete its folder.

**One thing worth knowing before you start.** Two installations can coexist, but
two logins cannot: the manufacturer's backend allows one session per account, so
while the new integration holds it the old one is logged out. Plan it as a
switch, not as a side-by-side trial.

**And one entity genuinely has no counterpart.** The two lines implemented the
windows as different kinds of entity - a cover here, a select there - so that one
cannot be matched up even by hand. It is one out of a hundred and ten, and it is
better said now than discovered later.
