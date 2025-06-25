import json

import aiohttp
import discord

import gspread_utilities as gu
from DB import DB


async def is_geoguessr_id_correct(geoguessr_id: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://www.geoguessr.com/api/v3/users/{geoguessr_id}"
        ) as response:
            if response.ok:
                return f":flag_{(await response.json())['countryCode'].lower()}:"
            else:
                return False


def flag_to_emoji(flag: str):
    flag_shortcodes_to_emojis = {
        ":flag_af:": "🇦🇫",  # Afghanistan
        ":flag_al:": "🇦🇱",  # Albanie
        ":flag_dz:": "🇩🇿",  # Algérie
        ":flag_ad:": "🇦🇩",  # Andorre
        ":flag_ao:": "🇦🇴",  # Angola
        ":flag_ag:": "🇦🇬",  # Antigua-et-Barbuda
        ":flag_ar:": "🇦🇷",  # Argentine
        ":flag_am:": "🇦🇲",  # Arménie
        ":flag_au:": "🇦🇺",  # Australie
        ":flag_at:": "🇦🇹",  # Autriche
        ":flag_az:": "🇦🇿",  # Azerbaïdjan
        ":flag_bs:": "🇧🇸",  # Bahamas
        ":flag_bh:": "🇧🇭",  # Bahreïn
        ":flag_bd:": "🇧🇩",  # Bangladesh
        ":flag_bb:": "🇧🇧",  # Barbade
        ":flag_by:": "🇧🇾",  # Bélarus
        ":flag_be:": "🇧🇪",  # Belgique
        ":flag_bz:": "🇧🇿",  # Belize
        ":flag_bj:": "🇧🇯",  # Bénin
        ":flag_bt:": "🇧🇹",  # Bhoutan
        ":flag_bo:": "🇧🇴",  # Bolivie
        ":flag_ba:": "🇧🇦",  # Bosnie-Herzégovine
        ":flag_bw:": "🇧🇼",  # Botswana
        ":flag_br:": "🇧🇷",  # Brésil
        ":flag_bn:": "🇧🇳",  # Brunéi
        ":flag_bg:": "🇧🇬",  # Bulgarie
        ":flag_bf:": "🇧🇫",  # Burkina Faso
        ":flag_bi:": "🇧🇮",  # Burundi
        ":flag_kh:": "🇰🇭",  # Cambodge
        ":flag_cm:": "🇨🇲",  # Cameroun
        ":flag_ca:": "🇨🇦",  # Canada
        ":flag_cv:": "🇨🇻",  # Cap-Vert
        ":flag_cf:": "🇨🇫",  # République centrafricaine
        ":flag_td:": "🇹🇩",  # Tchad
        ":flag_cl:": "🇨🇱",  # Chili
        ":flag_co:": "🇨🇴",  # Colombie
        ":flag_km:": "🇰🇲",  # Comores
        ":flag_cr:": "🇨🇷",  # Costa Rica
        ":flag_hr:": "🇭🇷",  # Croatie
        ":flag_cu:": "🇨🇺",  # Cuba
        ":flag_cy:": "🇨🇾",  # Chypre
        ":flag_cz:": "🇨🇿",  # Tchéquie
        ":flag_cd:": "🇨🇩",  # République démocratique du Congo
        ":flag_dk:": "🇩🇰",  # Danemark
        ":flag_dj:": "🇩🇯",  # Djibouti
        ":flag_dm:": "🇩🇲",  # Dominique
        ":flag_do:": "🇩🇴",  # République dominicaine
        ":flag_tl:": "🇹🇱",  # Timor oriental
        ":flag_ec:": "🇪🇨",  # Équateur
        ":flag_eg:": "🇪🇬",  # Égypte
        ":flag_sv:": "🇸🇻",  # Salvador
        ":flag_gq:": "🇬🇶",  # Guinée équatoriale
        ":flag_er:": "🇪🇷",  # Érythrée
        ":flag_ee:": "🇪🇪",  # Estonie
        ":flag_sz:": "🇸🇿",  # Eswatini
        ":flag_et:": "🇪🇹",  # Éthiopie
        ":flag_fj:": "🇫🇯",  # Fidji
        ":flag_fi:": "🇫🇮",  # Finlande
        ":flag_fr:": "🇫🇷",  # France
        ":flag_ga:": "🇬🇦",  # Gabon
        ":flag_ge:": "🇬🇪",  # Géorgie
        ":flag_de:": "🇩🇪",  # Allemagne
        ":flag_gh:": "🇬🇭",  # Ghana
        ":flag_gr:": "🇬🇷",  # Grèce
        ":flag_gd:": "🇬🇩",  # Grenade
        ":flag_gt:": "🇬🇹",  # Guatemala
        ":flag_gy:": "🇬🇾",  # Guyana
        ":flag_ht:": "🇭🇹",  # Haïti
        ":flag_hn:": "🇭🇳",  # Honduras
        ":flag_hu:": "🇭🇺",  # Hongrie
        ":flag_is:": "🇮🇸",  # Islande
        ":flag_in:": "🇮🇳",  # Inde
        ":flag_id:": "🇮🇩",  # Indonésie
        ":flag_ir:": "🇮🇷",  # Iran
        ":flag_iq:": "🇮🇶",  # Irak
        ":flag_ie:": "🇮🇪",  # Irlande
        ":flag_il:": "🇮🇱",  # Israël
        ":flag_it:": "🇮🇹",  # Italie
        ":flag_ci:": "🇨🇮",  # Côte d’Ivoire
        ":flag_jm:": "🇯🇲",  # Jamaïque
        ":flag_jp:": "🇯🇵",  # Japon
        ":flag_jo:": "🇯🇴",  # Jordanie
        ":flag_kz:": "🇰🇿",  # Kazakhstan
        ":flag_ke:": "🇰🇪",  # Kenya
        ":flag_ki:": "🇰🇮",  # Kiribati
        ":flag_kw:": "🇰🇼",  # Koweït
        ":flag_kg:": "🇰🇬",  # Kirghizistan
        ":flag_la:": "🇱🇦",  # Laos
        ":flag_lv:": "🇱🇻",  # Lettonie
        ":flag_lb:": "🇱🇧",  # Liban
        ":flag_ls:": "🇱🇸",  # Lesotho
        ":flag_lr:": "🇱🇷",  # Libéria
        ":flag_ly:": "🇱🇾",  # Libye
        ":flag_li:": "🇱🇮",  # Liechtenstein
        ":flag_lt:": "🇱🇹",  # Lituanie
        ":flag_lu:": "🇱🇺",  # Luxembourg
        ":flag_mg:": "🇲🇬",  # Madagascar
        ":flag_mw:": "🇲🇼",  # Malawi
        ":flag_my:": "🇲🇾",  # Malaisie
        ":flag_mv:": "🇲🇻",  # Maldives
        ":flag_ml:": "🇲🇱",  # Mali
        ":flag_mt:": "🇲🇹",  # Malte
        ":flag_mh:": "🇲🇭",  # Îles Marshall
        ":flag_mr:": "🇲🇷",  # Mauritanie
        ":flag_mu:": "🇲🇺",  # Maurice
        ":flag_mx:": "🇲🇽",  # Mexique
        ":flag_fm:": "🇫🇲",  # États fédérés de Micronésie
        ":flag_md:": "🇲🇩",  # Moldavie
        ":flag_mc:": "🇲🇨",  # Monaco
        ":flag_mn:": "🇲🇳",  # Mongolie
        ":flag_me:": "🇲🇪",  # Monténégro
        ":flag_ma:": "🇲🇦",  # Maroc
        ":flag_mz:": "🇲🇿",  # Mozambique
        ":flag_mm:": "🇲🇲",  # Myanmar
        ":flag_na:": "🇳🇦",  # Namibie
        ":flag_nr:": "🇳🇷",  # Nauru
        ":flag_np:": "🇳🇵",  # Népal
        ":flag_nl:": "🇳🇱",  # Pays-Bas
        ":flag_nz:": "🇳🇿",  # Nouvelle-Zélande
        ":flag_ni:": "🇳🇮",  # Nicaragua
        ":flag_ne:": "🇳🇪",  # Niger
        ":flag_ng:": "🇳🇬",  # Nigeria
        ":flag_kp:": "🇰🇵",  # Corée du Nord
        ":flag_mk:": "🇲🇰",  # Macédoine du Nord
        ":flag_no:": "🇳🇴",  # Norvège
        ":flag_om:": "🇴🇲",  # Oman
        ":flag_pk:": "🇵🇰",  # Pakistan
        ":flag_pw:": "🇵🇼",  # Palaos
        ":flag_pa:": "🇵🇦",  # Panama
        ":flag_pg:": "🇵🇬",  # Papouasie-Nouvelle-Guinée
        ":flag_py:": "🇵🇾",  # Paraguay
        ":flag_pe:": "🇵🇪",  # Pérou
        ":flag_ph:": "🇵🇭",  # Philippines
        ":flag_pl:": "🇵🇱",  # Pologne
        ":flag_pt:": "🇵🇹",  # Portugal
        ":flag_qa:": "🇶🇦",  # Qatar
        ":flag_cg:": "🇨🇬",  # Congo
        ":flag_ro:": "🇷🇴",  # Roumanie
        ":flag_ru:": "🇷🇺",  # Russie
        ":flag_rw:": "🇷🇼",  # Rwanda
        ":flag_kn:": "🇰🇳",  # Saint-Kitts-et-Nevis
        ":flag_lc:": "🇱🇨",  # Sainte-Lucie
        ":flag_vc:": "🇻🇨",  # Saint-Vincent-et-les-Grenadines
        ":flag_sm:": "🇸🇲",  # Saint-Marin
        ":flag_st:": "🇸🇹",  # Sao Tomé-et-Principe
        ":flag_sa:": "🇸🇦",  # Arabie Saoudite
        ":flag_sn:": "🇸🇳",  # Sénégal
        ":flag_rs:": "🇷🇸",  # Serbie
        ":flag_sc:": "🇸🇨",  # Seychelles
        ":flag_sl:": "🇸🇱",  # Sierra Leone
        ":flag_sg:": "🇸🇬",  # Singapour
        ":flag_sk:": "🇸🇰",  # Slovaquie
        ":flag_si:": "🇸🇮",  # Slovénie
        ":flag_sb:": "🇸🇧",  # Îles Salomon
        ":flag_so:": "🇸🇴",  # Somalie
        ":flag_za:": "🇿🇦",  # Afrique du Sud
        ":flag_kr:": "🇰🇷",  # Corée du Sud
        ":flag_ss:": "🇸🇸",  # Soudan du Sud
        ":flag_es:": "🇪🇸",  # Espagne
        ":flag_lk:": "🇱🇰",  # Sri Lanka
        ":flag_sd:": "🇸🇩",  # Soudan
        ":flag_sr:": "🇸🇷",  # Suriname
        ":flag_se:": "🇸🇪",  # Suède
        ":flag_ch:": "🇨🇭",  # Suisse
        ":flag_sy:": "🇸🇾",  # Syrie
        ":flag_tj:": "🇹🇯",  # Tadjikistan
        ":flag_tz:": "🇹🇿",  # Tanzanie
        ":flag_th:": "🇹🇭",  # Thaïlande
        ":flag_gm:": "🇬🇲",  # Gambie
        ":flag_tg:": "🇹🇬",  # Togo
        ":flag_to:": "🇹🇴",  # Tonga
        ":flag_tt:": "🇹🇹",  # Trinité-et-Trinbago
        ":flag_tn:": "🇹🇳",  # Tunisie
        ":flag_tr:": "🇹🇷",  # Turquie
        ":flag_tm:": "🇹🇲",  # Turkménistan
        ":flag_tv:": "🇹🇻",  # Tuvalu
        ":flag_ug:": "🇺🇬",  # Ouganda
        ":flag_ua:": "🇺🇦",  # Ukraine
        ":flag_ae:": "🇦🇪",  # Émirats arabes unis
        ":flag_gb:": "🇬🇧",  # Royaume-Uni
        ":flag_us:": "🇺🇸",  # États-Unis d’Amérique
        ":flag_uy:": "🇺🇾",  # Uruguay
        ":flag_uz:": "🇺🇿",  # Ouzbékistan
        ":flag_vu:": "🇻🇺",  # Vanuatu
        ":flag_ve:": "🇻🇪",  # Venezuela
        ":flag_vn:": "🇻🇳",  # Vietnam
        ":flag_ye:": "🇾🇪",  # Yémen
        ":flag_zm:": "🇿🇲",  # Zambie
        ":flag_zw:": "🇿🇼",  # Zimbabwe
        ":flag_cn:": "🇨🇳",  # Chine
    }
    return flag_shortcodes_to_emojis[flag]


def get_flag(discordId: int):
    inscriptionData = json.load(open("inscriptions.json", "r"))
    return flag_to_emoji(inscriptionData["players"][str(discordId)]["flag"])


async def inscription(member: dict):
    inscriptionData = json.load(open("inscriptions.json", "r"))
    inscriptionData["players"][member["discordId"]] = member
    json.dump(inscriptionData, open("inscriptions.json", "w"))


def team_already_exists(member1: discord.Member, member2: discord.Member):
    inscriptionData = json.load(open("inscriptions.json", "r"))
    return (
        f"{member1.id}_{member2.id}" in inscriptionData["teams"]
        or f"{member2.id}_{member1.id}" in inscriptionData["teams"]
    )


async def create_team(member1: discord.Member, member2: discord.Member):
    inscriptionData = json.load(open("inscriptions.json", "r"))
    member1 = inscriptionData["players"][str(member1.id)]
    member2 = inscriptionData["players"][str(member2.id)]
    inscriptionData["teams"][f"{member1['discordId']}_{member2['discordId']}"] = [
        member1,
        member2,
    ]
    json.dump(inscriptionData, open("inscriptions.json", "w"))
    return member1["surname"], member2["surname"]

async def get_qualified_teams():
    return await gu.get_qualified_teams_names()


async def get_bets_discordIds():
    return await gu.get_bets_discordIds()


async def place_bet(
    discordId: int, bet1: str, bet2: str, bet3: str, isAnonymous: bool, discordName: str
):
    await gu.place_bet(discordId, bet1, bet2, bet3, isAnonymous, discordName)
