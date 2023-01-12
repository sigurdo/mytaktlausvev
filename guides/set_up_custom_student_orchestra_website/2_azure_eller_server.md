# Fullstendig vegvisar for å setje opp eigen studentorchestervev

## Valg av type hosting

MyTaktlausvev støtter 2 fundamentalt ulike typar hosting:

- `azure`: Avansert cloud hosting hos [Azure](https://azure.microsoft.com/en-us/).
- `server`: Meir konvensjonell hosting med Docker-konteinere på en Linux-server.

`azure` er den typen hosting Taktlausveven brukar og vert anbefala hvis du vil ha den sikraste og mest skalerbare hostinga du kan få. Oppsettet av Azure-hosting er dessverre ikkje dokumentert skritt-for-skritt og du må sette deg inn i alt det tekniske sjølv. Ein beskriving av kva for infrastruktur ein må setje opp finnast på den offisielle [Taktlausvev-wikien](https://gitlab.com/taktlause/taktlausveven/-/wikis/Azure).

`server` er den typen hosting vi har skritt-for-skritt-dokumentasjon for og vert anbefala hvis du vil gjere det enkelt.

Det som gjer `azure`-hostinga betre, men óg meir avansert enn `server`-hostinga er at tenestane database, fillagring og bildelagring vert utført separat frå kvarandre og frå django-koden. I cloud-hosting-verda brukar ein dedikerte skalerbare løysingar for slike tenestar, i staden for ein vanleg Linux-server. Med `server`-hosting vert alle tenestane utført på ein og same Linux-server og alt vert i mykje større grad sett opp automatisk.

[Forrige side](1_forkunnskapar.md) | [Neste side (`azure`)](azure_3_skaffe_azure_tilgang.md) | [Neste side (`server`)](server_3_skaffe_linux_server.md)
