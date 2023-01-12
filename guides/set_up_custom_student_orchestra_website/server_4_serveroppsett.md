# Fullstendig vegvisar for å setje opp eigen studentorchestervev

## Grunnleggjande serveroppsett

For øka sikkerheit bør du gjere følgande ting:

- Setje opp ein vanleg brukar slik at du ikkje må logge inn som `root` kvar gong du skal gjere noko.
- Aktivere SSH `PubkeyAuthentication`, deaktivere SSH `PasswordAuthentication` og deaktivere SSH `PermitRootLogin`.
- Setje opp ein brannmur som sperrar alle incoming requests til andre portar enn 22 (SSH), 80 (HTTP) og 443 (HTTPS).
- Setje opp [`fail2ban`](https://www.fail2ban.org/wiki/index.php/Main_Page) til å automatisk svarteliste IP-addresser som framstår ondsinna ved å til dømes gjere mange innloggingsforsøk med feil passord.

Ingen av desse tinga er nødvendig for å få veven opp og kjøre, og forhåpentlegvis klarer ingen å hacke seg inn på serveren din uansett, men om du sett opp alt dette er serveren i praksis mykje sikrare. Dessverre er mange av tinga litt kompliserte å forklare korleis ein gjer, så vi kjem derfor berre til å forklare korleis ein sett opp brannmur.

### Brannmur

```
apt install ufw
ufw default deny incoming
ufw default allow outgoing
ufw allow 22
ufw allow 80
ufw allow 443
ufw enable
```

[Forrige side](server_3_skaffe_linux_server.md) | [Neste side](server_5_mytaktlausvev_repo.md)
