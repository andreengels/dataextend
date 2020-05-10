#!/usr/bin/python
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot.data import sparql
import sys, re
import codecs
import datetime
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from urllib.parse import unquote, urlencode
from urllib.parse import quote as encode
import ssl
from collections import defaultdict
from html import unescape

FORCE = True

class DataExtendBot:
    QRE = re.compile('Q\d+$')
    PQRE = re.compile('[PQ]\d+$')
    def __init__(self):
        self.labels = {}
        self.data = defaultdict(dict)
        self.noname = []
        self.labelfile = "labels.txt"
        self.datafile = "defaultdata.txt"
        self.nonamefile = "noname.txt"
        self.loaddata()
        self.site = pywikibot.Site().data_repository()
        self.analyzertype = {
            "P213": IsniAnalyzer,
            "P214": ViafAnalyzer,
            "P227": GndAnalyzer,
            "P244": LcAuthAnalyzer,
            "P245": UlanAnalyzer,
            "P268": BnfAnalyzer,
            "P269": SudocAnalyzer,
            "P271": CiniiAnalyzer,
            "P345": ImdbAnalyzer,
            "P396": SbnAnalyzer,
            "P409": LibrariesAustraliaAnalyzer,
            "P434": MusicBrainzAnalyzer,
            "P454": StructuraeAnalyzer,
            "P496": OrcidAnalyzer,
            "P497": CbdbAnalyzer,
            "P535": FindGraveAnalyzer,
            "P549": MathGenAnalyzer,
            "P586": IpniAuthorsAnalyzer,
            #"P590": GnisAnalyzer, <http redirect loop>
            "P648": OpenLibraryAnalyzer,
            "P650": RkdArtistsAnalyzer,
            "P651": BiografischPortaalAnalyzer,
            "P691": NkcrAnalyzer,
            "P723": DbnlAnalyzer,
            "P781": SikartAnalyzer,
            "P839": ImslpAnalyzer,
            "P902": HdsAnalyzer,
            "P906": SelibrAnalyzer,
            "P950": BneAnalyzer,
            "P1005": PtbnpAnalyzer,
            #"P1006": NtaAnalyzer,
            "P1015": BibsysAnalyzer,
            "P1138": KunstindeksAnalyzer,
            "P1146": IaafAnalyzer,
            #"P1153": ScopusAnalyzer, <requires login>
            "P1185": RodovidAnalyzer,
            "P1220": IbdbAnalyzer,
            "P1233": IsfdbAnalyzer,
            "P1263": NndbAnalyzer,
            "P1280": ConorAnalyzer,
            "P1284": MunzingerAnalyzer,
            #"P1305": SkyScraperAnalyzer, <forbidden>
            "P1315": PeopleAustraliaAnalyzer,
            "P1367": ArtUkAnalyzer,
            "P1368": LnbAnalyzer,
            "P1415": OxfordAnalyzer,
            "P1422": SandrartAnalyzer,
            "P1440": FideAnalyzer,
            "P1447": SportsReferenceAnalyzer,
            "P1463": PrdlAnalyzer,
            "P1469": FifaAnalyzer,
            "P1556": ZbmathAnalyzer,
            "P1580": UBarcelonaAnalyzer,
            "P1607": DialnetAnalyzer,
            "P1615": ClaraAnalyzer,
            "P1648": WelshBioAnalyzer,
            "P1667": TgnAnalyzer,
            #"P1695": NlpAnalyzer, <id doesn't work anymore>
            "P1707": DaaoAnalyzer,
            "P1741": GtaaAnalyzer,
            "P1749": ParlementPolitiekAnalyzer,
            "P1795": AmericanArtAnalyzer,
            "P1802": EmloAnalyzer,
            "P1816": NpgPersonAnalyzer,
            "P1819": GenealogicsAnalyzer,
            "P1838": PssBuildingAnalyzer,
            "P1871": CerlAnalyzer,
            "P1953": DiscogsAnalyzer,
            "P1986": ItalianPeopleAnalyzer,
            "P1988": DelargeAnalyzer,
            "P2005": HalensisAnalyzer,
            "P2016": AcademiaeGroninganaeAnalyzer,
            "P2029": UlsterAnalyzer,
            "P2041": NgvAnalyzer,
            "P2089": JukeboxAnalyzer,
            "P2163": FastAnalyzer,
            "P2168": SvenskFilmAnalyzer,
            "P2191": NilfAnalyzer,
            "P2252": NgaAnalyzer,
            "P2268": OrsayAnalyzer,
            "P2332": ArtHistoriansAnalyzer,
            "P2340": CesarAnalyzer,
            "P2342": AgorhaAnalyzer,
            "P2372": OdisAnalyzer,
            "P2381": AcademicTreeAnalyzer,
            "P2383": CthsAnalyzer,
            "P2446": TransfermarktAnalyzer,
            "P2454": KnawAnalyzer,
            "P2456": DblpAnalyzer,
            "P2469": TheatricaliaAnalyzer,
            #"P2533": WomenWritersAnalyzer, #fully opaque
            "P2604": KinopoiskAnalyzer,
            "P2605": CsfdAnalyzer, #<can't unpack https?>
            "P2639": FilmportalAnalyzer,
            "P2728": CageMatchAnalyzer,
            "P2732": PerseeAnalyzer,
            "P2750": PhotographersAnalyzer,
            "P2753": CanadianBiographyAnalyzer,
            "P2829": IWDAnalyzer,
            "P2843": BenezitAnalyzer,
            "P2915": EcarticoAnalyzer,
            "P2940": RostochiensiumAnalyzer,
            "P2941": MunksRollAnalyzer,
            "P2944": PlarrAnalyzer,
            "P2945": BookTradeAnalyzer,
            "P2949": WikitreeAnalyzer,
            "P2963": GoodreadsAnalyzer,
            "P2977": LbtAnalyzer,
            "P3029": NationalArchivesAnalyzer,
            "P3107": LdifAnalyzer,
            "P3109": PeakbaggerAnalyzer,
            "P3138": OfdbAnalyzer,
            "P3154": RunebergAuthorAnalyzer,
            "P3159": UGentAnalyzer,
            "P3283": BandcampAnalyzer,
            "P3346": HkmdbAnalyzer,
            "P3360": NobelPrizeAnalyzer,
            "P3392": SurmanAnalyzer,
            "P3410": CcedAnalyzer,
            "P3429": EnlightenmentAnalyzer,
            "P3430": SnacAnalyzer,
            "P3630": BabelioAnalyzer,
            "P3782": ArtnetAnalyzer,
            "P3786": DanskefilmAnalyzer,
            "P3788": BnaAnalyzer,
            "P3790": AnimeConsAnalyzer,
            "P3829": PublonsAnalyzer,
            "P3844": SynchronkarteiAnalyzer,
            "P3924": TrackFieldFemaleAnalyzer,
            "P3925": TrackFieldMaleAnalyzer,
            "P4124": WhosWhoFranceAnalyzer,
            "P4145": AthenaeumAnalyzer,
            "P4206": FoihAnalyzer,
            "P4228": EoasAnalyzer,
            #"P4293": PM20Analyzer, <content in frame with unclear url>
            "P4399": ItauAnalyzer,
            "P4459": SpanishBiographyAnalyzer,
            "P4548": CommonwealthGamesAnalyzer,
            "P4629": OnlineBooksAnalyzer,
            "P4657": NumbersAnalyzer,
            "P4663": DacsAnalyzer,
            "P4666": CinemagiaAnalyzer, #<unclear redirection>
            "P4687": PeintresBelgesAnalyzer,
            "P4749": AuteursLuxembourgAnalyzer,
            "P4759": LuminousAnalyzer,
            #"P4823": AmericanBiographyAnalyzer, <503>
            "P4872": GeprisAnalyzer,
            "P4887": WebumeniaAnalyzer,
            #"P4927": InvaluableAnalyzer, <unable to load>
            "P4929": AinmAnalyzer,
            "P4985": TmdbAnalyzer,
            #"P5034": LibraryKoreaAnalyzer, <doesnt load>
            "P5068": KunstenpuntAnalyzer,
            "P5239": ArtistsCanadaAnalyzer,
            "P5246": PornhubAnalyzer,
            "P5267": YoupornAnalyzer,
            "P5273": NelsonAtkinsAnalyzer,
            "P5329": ArmbAnalyzer,
            "P5359": OperoneAnalyzer,
            "P5361": BnbAnalyzer,
            "P5365": InternetBookAnalyzer,
            "P5375": BiuSanteAnalyzer,
            "P5394": PoetsWritersAnalyzer,
            "P5308": ScottishArchitectsAnalyzer,
            "P5357": SFAnalyzer,
            "P5368": NatGeoCanadaAnalyzer,
            "P5408": FantasticFictionAnalyzer,
            "P5415": WhonameditAnalyzer,
            "P5421": TradingCardAnalyzer,
            "P5491": BedethequeAnalyzer,
            "P5534": OmdbAnalyzer,
            "P5570": NoosfereAnalyzer,
            "P5597": ArtcyclopediaAnalyzer,
            "P5645": AcademieFrancaiseAnalyzer,
            "P5731": AngelicumAnalyzer,
            "P5739": PuscAnalyzer,
            "P5747": CwaAnalyzer,
            #"P6127": LetterboxdAnalyzer, 
            "P6167": BritishExecutionsAnalyzer,
            'P6188': BdfaAnalyzer,
            "P6194": AustrianBiographicalAnalyzer,
            "P6231": BdelAnalyzer,
            "P6517": WhoSampledAnalyzer,
            "P6578": MutualAnalyzer,
            "P6844": AbartAnalyzer,
            "P6873": IntraTextAnalyzer,
            "P7032": RepertoriumAnalyzer,
            "Wiki": WikiAnalyzer,
            "www.deutsche-biographie.de": DeutscheBiographieAnalyzer,
            "www.brooklynmuseum.org": BrooklynMuseumAnalyzer,
            "kunstaspekte.art": KunstaspekteAnalyzer,
            "www.nationaltrustcollections.org.uk": NationalTrustAnalyzer,
            "www.oxfordartonline.com": BenezitUrlAnalyzer,
            "exhibitions.univie.ac.at": UnivieAnalyzer,
            "weber-gesamtausgabe.de": WeberAnalyzer,
            "Data": BacklinkAnalyzer,
            }

    def label(self, title):
        if title.startswith("!date!"):
            return self.showtime(self.createdateclaim(title[6:]))
        elif title.startswith("!q!"):
            return title[3:]
        elif not self.PQRE.match(title):
            return title
        if title in self.labels:
            return self.labels[title]
        item = self.page(title)
        label = None
        try:
            labels = item.get()['labels']
        except pywikibot.NoPage:
            labels = {}
        for lang in ['en','nl','de','fr','es','it','af','nds','li','vls','zea','fy','no','sv','da','pt','ro','pl','cs','sk','hr','et','fi','lt','lv','tr','cy']:
            if lang in labels:
                try:
                    label = labels[lang]['value']
                except TypeError:
                    label = labels[lang]
                break
        else:
            label = title
        self.labels[title] = label
        return label

    def loaddata(self):
        try:
            with codecs.open(self.labelfile, 'r', 'utf-8') as f:
                for line in f.readlines():
                    (key,value) = line.strip().split(":", 1)
                    self.labels[key] = value
        except IOError:
            pass
        try:
            with codecs.open(self.datafile, 'r', 'utf-8') as f:
                for line in f.readlines():
                    parts = line.strip().split(':')
                    try:
                        (dtype, key, value) = parts
                    except ValueError:
                        (dtype, key, value) = (parts[0], ':'.join(parts[1:-1]), parts[-1])
                    self.data[dtype][key] = value
        except IOError:
            pass
        try:
            with codecs.open(self.nonamefile, 'r', 'utf-8') as f:
                for line in f.readlines():
                    self.noname.append(line.strip())
        except IOError:
            pass

    def savedata(self):
        with codecs.open(self.labelfile, 'w', 'utf-8') as f:
            for item in self.labels:
                f.write("%s:%s\n"%(item, self.labels[item]))
        with codecs.open(self.datafile, 'w', 'utf-8') as f:
            for dtype in self.data:
                for key in self.data[dtype]:
                    f.write("%s:%s:%s\n"%(dtype, key, self.data[dtype][key]))
        with codecs.open(self.nonamefile, 'w', 'utf-8') as f:
            for noname in set(self.noname):
                f.write("%s\n"%noname)

    def page(self, title):
        title = title.split(':')[-1]
        if title.startswith('Q'):
            return pywikibot.ItemPage(self.site, title)
        elif title.startswith('P'):
            return pywikibot.PropertyPage(self.site, title)
        else:
            raise ValueError

    def showtime(self, time):
        if time is None:
            return "unknown"
        result = str(time.year)
        if time.precision < 9:
            result = "ca. " + result
        if time.precision >=10:
            result = "%s-%s"%(time.month, result)
        if time.precision >=11:
            result = "%s-%s"%(time.day, result)
        if time.precision >=12:
            result = "%s %s"%(result, time.hour)
        if time.precision >=13:
            result = "%s:%s"%(result, time.minute)
        if time.precision >=14:
            result = "%s:%s"%(result, time.second)
        return result

    def showclaims(self, claims):
        for prop in claims:
            for claim in claims[prop]:
                if claim.type == "wikibase-item":
                    if claim.getTarget() == None:
                        pywikibot.output("%s: unknown"%(self.label(prop)))
                    else:
                        pywikibot.output("%s: %s"%(self.label(prop), self.label(claim.getTarget().title())))
                elif claim.type == "time":
                    pywikibot.output("%s: %s"%(self.label(prop), self.showtime(claim.getTarget())))
                elif claim.type in ["external-id", "commonsMedia"]:
                    pywikibot.output("%s: %s"%(self.label(prop), claim.getTarget()))
                elif claim.type == "quantity":
                    pywikibot.output("%s: %s %s"%(self.label(prop), claim.getTarget().amount, self.label(claim.getTarget().unit.split('/')[-1])))
                else:
                    pywikibot.output("Unknown type {} for property {}".format(claim.type, self.label(prop)))

    MONTHNUMBER = {
        "1": 1, "01": 1, "i": 1,
        "2": 2, "02": 2, "ii": 2,
        "3": 3, "03": 3, "iii": 3,
        "4": 4, "04": 4, "iv": 4,
        "5": 5, "05": 5, "v": 5,
        "6": 6, "06": 6, "vi": 6,
        "7": 7, "07": 7, "vii": 7,
        "8": 8, "08": 8, "viii": 8,
        "9": 9, "09": 9, "ix": 9,
        "10": 10, "x": 10,
        "11": 11, "xi": 11,
        "12": 12, "xii": 12,
        "january": 1, "jan": 1,
        "february": 2, "feb": 2, "febr": 2,
        "march": 3, "mar": 3,
        "april": 4, "apr": 4,
        "may": 5,
        "june": 6, "jun": 6,
        "july": 7, "jul": 7,
        "august": 8, "aug": 8,
        "september": 9, "sep": 9, "sept": 9,
        "october": 10, "oct": 10,
        "november": 11, "nov": 11,
        "december": 12, "dec": 12,
        "gennaio": 1, "gen": 1, "genn": 1,
        "febbraio": 2, "febb": 2, "febbr": 2,
        "marzo": 3, "marz": 3,
        "aprile": 4,
        "maggio": 5, "mag": 5, "magg": 5,
        "giugno": 6, "giu": 6,
        "luglio": 7, "lug": 7, "lugl": 7,
        "agosto": 8, "ago": 8, "agost": 8, "ag": 8,
        "settembre": 9, "set": 9, "sett": 9,
        "ottobre": 10, "ott": 10, "otto": 10,
        "novembre": 11,
        "dicembre": 12, "dic": 12,
        "januari": 1,
        "februari": 2,
        "maart": 3, "maa": 3,
        "mei": 5,
        "juni": 6,
        "juli": 7,
        "augustus": 8,
        "oktober": 10, "okt": 10,
        "janvier": 1,
        "février": 2, "fevrier": 2, "fév": 2, "fev": 2, "f\\xe9vrier": 2,
        "mars": 3,
        "avril": 4, "avr": 4,
        "mai": 5,
        "juin": 6,
        "juillet": 7,
        "août": 8, "aout": 8, "aoû": 8, "aou": 8,
        "septembre": 9,
        "octobre": 10,
        "novembre": 11,
        "décembre": 12, "déc": 12,
        "januar": 1, "jänner": 1,
        "februar": 2,
        "märz": 3, "m\\xe4rz": 3,
        "mai": 5,
        "dezember": 12, "dez": 12,
        "eanáir": 1, "eanair": 1,
        "feabhra": 2,
        "márta": 3, "marta": 3,
        "aibreán": 4, "aibrean": 4,
        "bealtaine": 5,
        "meitheamh": 6,
        "iúil": 7, "iuil": 7,
        "lúnasa": 8, "lunasa": 8,
        "meán fómhair": 9, "mean fomhair": 9,
        "deireadh fómhair": 10, "deireadh fomhair": 10,
        "samhain": 11,
        "nollaig": 12,
        "styczeń": 1, "stycznia": 1,
        "luty": 2, "lutego": 2,
        "marzec": 3, "marca": 3,
        "kwiecień": 4, "kwietnia": 4,
        "maj": 5, "maja": 5,
        "czerwiec": 6, "czerwca": 6,
        "lipiec": 7, "lipca": 7,
        "sierpień": 8, "sierpnia": 8,
        "wrzesień": 9, "września": 9,
        "październik": 10, "października": 10,
        "listopad": 11, "listopada": 11,
        "grudzień": 12, "grudnia": 12,
        "enero": 1,
        "febrero": 2,
        "marzo": 3,
        "abril": 4,
        "mayo": 5,
        "junio": 6,
        "julio": 7,
        "agosto": 8,
        "septiembre": 9,
        "octubre": 10,
        "noviembre": 11,
        "diciembre": 12,
        }

    def createdateclaim(self, text):
        text = text.strip()
        year = None
        month = None
        day = None
        if re.match("\d{,4}(?:年頃)?$", text):
            year = int(text)
            month = None
            day = None
        if re.match("(?:1\d{3}|20[01]\d)[01]\d[0123]\d$", text):
            year = int(text[:4])
            month = int(text[4:6])
            day = int(text[6:])
        if re.match("\d{4}-\d{2}$", text):
            year = int(text[:4])
            month = int(text[-2:])
        m = re.match("(\d{1,2})-(\d{4})", text)
        if m:
            year = int(m.group(2))
            month = int(m.group(1))
        m = re.match("(\d+)[-\./\|](\d{1,2})[-./\|](\d{1,2})$", text)
        if m:
            year = int(m.group(1))
            month = int(m.group(2))
            day = int(m.group(3))
        m = re.match("(\d{1,2})[-\./\|]\s*(\d{1,2})[-\./\|]\s*(\d{3,4})\.?$", text)
        if m:
            year = int(m.group(3))
            month = int(m.group(2))
            day = int(m.group(1))
        m = re.match("(\d{1,2})[-\./\s]([iIvVxX]+)[-\./\s](\d{4})$", text)
        if m:
            year = int(m.group(3))
            try:
                month = self.MONTHNUMBER[m.group(2).lower()]
            except KeyError:
                raise ValueError("Don't know month {}".format(m.group(2)))
            day = int(m.group(1))
        m = re.match("(\d+)(?:\.|er|eme|ème)?[\s\.]\s*([^\s\.]{3,})\.?[\s\.]\s*(\d+)$", text)
        if m:
            year = int(m.group(3))
            try:
                month = self.MONTHNUMBER[m.group(2).lower()]
            except KeyError:
                raise ValueError("Don't know month {}".format(m.group(2)))
            day = int(m.group(1))
        m = re.match("(\d{4})\.?[\s\.]\s*([^\s\.]{3,})\.?[\s\.]\s*(\d+)$", text)
        if m:
            year = int(m.group(1))
            try:
                month = self.MONTHNUMBER[m.group(2).lower()]
            except KeyError:
                raise ValueError("Don't know month {}".format(m.group(2)))
            day = int(m.group(3))
        m = re.match("(\d+)(?: de)? (\w+[a-z]\w+) de (\d+)", text)
        if m:
            year = int(m.group(3))
            try:
                month = self.MONTHNUMBER[m.group(2).lower()]
            except KeyError:
                raise ValueError("Don't know month {}".format(m.group(2)))
            day = int(m.group(1))        
        m = re.match("(\w*[a-zA-Z]\w*)\.? (\d+)$", text)
        if m:
            year = int(m.group(2))
            try:
                month = self.MONTHNUMBER[m.group(1).lower()]
            except KeyError:
                raise ValueError("Don't know month {}".format(m.group(1)))
        m = re.match("(\w+)\.? (\d{1,2})(?:st|nd|rd|th)?\.?\s*,\s*(\d{3,4})$", text)
        if m:
            year = int(m.group(3))
            try:
                month = self.MONTHNUMBER[m.group(1).lower()]
            except KeyError:
                raise ValueError("Don't know month {}".format(m.group(1)))
            day = int(m.group(2))
        m = re.match('(\d{4}),? (\d{1,2}) (\w+)', text)
        if m:
            year = int(m.group(1))
            try:
                month = self.MONTHNUMBER[m.group(3).lower()]
            except KeyError:
                raise ValueError("Don't know month {}".format(m.group(1)))
            day = int(m.group(2))
        m = re.match('(\d+)年(\d+)月(\d+)日', text)
        if m:
            year = int(m.group(1))
            month = int(m.group(2))
            day = int(m.group(3))
        m = re.match('(\d+)年$', text)
        if m:
            year = int(m.group(1))
        if day == 0: day = None
        if day is None and month == 0: month = None
        if month and month > 12:
            raise ValueError('Date seems to have an invalid month number {}'.format(month))
        if day and day > 31:
            raise ValueError('Date seems to have an invalid day number {}'.format(day))
        if not year:
            raise ValueError("Can't interpret date {}".format(text))
        return pywikibot.WbTime(year=year, month=month, day=day, precision=9 if month is None else 10 if day is None else 11)

    QUANTITYTYPE = {
        "meter": "Q11573", "metre": "Q11573", "m": "Q11573", "meters": "Q11573", "metres": "Q11573", "м": "Q11573",
        "centimeter": "Q174728", "centimetre": "Q174728", "cm": "Q174728",
        "foot": "Q3710", "feet": "Q3710", "ft": "Q3710",
        "mile": "Q253276", "mi": "Q253276",
        "kilometer": "Q828224", "kilometre": "Q828224", "km": "Q828224",
        "minute": "Q7727", "minutes": "Q7727", "min": "Q7727", "minuten": "Q7727",
        "second": "Q11574", "s": "Q11574",
        "kilogram": "Q11570", "kg": "Q11570",
        "lb": "Q100995", "lbs": "Q100995", "pond": "Q100995",
        }

    def createquantityclaim(self, text):
        m = re.match("(\d+(?:\.\d+)?)\s*(\w+)", text.replace(',', '.'))
        amount = m.group(1)
        name = m.group(2).lower()
        return pywikibot.WbQuantity(amount, unit=pywikibot.ItemPage(self.site, self.QUANTITYTYPE[name]), site=self.site)

    def workon(self, item, restrict=None):
        try:
            longtexts = []
            item.get()
            pywikibot.output("Current information:")
            claims = item.claims
            descriptions = item.descriptions
            labels = item.labels
            aliases = item.aliases
            newdescriptions = defaultdict(set)
            updatedclaims = {
                prop: claims[prop]
                for prop in claims
                }
            self.showclaims(claims)
            dorestrict = True
            continueafterrestrict = False
            if restrict and restrict.endswith('+'):
                restrict = restrict[:-1]
                continueafterrestrict = True
            if restrict and restrict.endswith('*'):
                restrict = restrict[:-1]
                dorestrict = False
                continueafterrestrict = True              
            unidentifiedprops = []
            claims['Wiki'] = [Quasiclaim(page.title(force_interwiki=True, as_link=True)[2:-2]) for page in item.iterlinks()]
            claims['Data'] = [Quasiclaim(item.title())]
            propstodo = list(claims)
            propsdone = []
            while propstodo:
                if propsdone:
                    item.get(force=True)
                    claims = item.claims
                    claims['Wiki'] = [Quasiclaim(page.title(force_interwiki=True, as_link=True)[2:-2]) for page in item.iterlinks()]
                    descriptions = item.descriptions
                    labels = item.labels
                    aliases = item.aliases
                propsdone += propstodo
                propstodonow = propstodo[:]
                propstodo = []
                for prop in propstodonow:
                    if prop not in claims.keys(): # No idea how this can happen, but apparently it can
                        continue
                    if restrict:
                        if prop != restrict:
                            continue
                        elif continueafterrestrict:
                            restrict = None
                        if not dorestrict:
                            continue
                    for mainclaim in claims[prop]:
                        if mainclaim.type == "external-id" or prop == "P973":
                            identifier = mainclaim.getTarget()
                            try:
                                if prop == "P973":
                                    analyzertype = self.analyzertype[identifier.split("/")[2]]
                                else:
                                    analyzertype = self.analyzertype[prop]
                            except KeyError:
                                unidentifiedprops.append(prop)
                            else:
                                analyzer = analyzertype(identifier, self.data, item.title())
                                newclaims = analyzer.findclaims() or []
                                if FORCE:
                                    result = ''
                                else:
                                    pywikibot.output("Found here:")
                                    for claim in newclaims:
                                        pywikibot.output("{}: {}".format(self.label(claim[0]), self.label(claim[1])))
                                    result = input("Save this? (Y/n) ")
                                if (not result) or result[0].upper() != "N":
                                    for claim in newclaims:
                                        if claim[0] in updatedclaims and self.isinclaims(claim[1], updatedclaims[claim[0]]):
                                            if claim[2]:
                                                if claim[2].dbid:
                                                    if claim[2].iswiki:
                                                        source = pywikibot.Claim(self.site, 'P143')
                                                    else:
                                                        source = pywikibot.Claim(self.site, 'P248')
                                                    source.setTarget(pywikibot.ItemPage(self.site, claim[2].dbid))
                                                else:
                                                    source = None
                                                if claim[2].iswiki:
                                                    url = pywikibot.Claim(self.site, 'P4656')
                                                else:
                                                    url = pywikibot.Claim(self.site, 'P854')
                                                if claim[2].sparqlquery:
                                                    url.setTarget(pywikibot.ItemPage(self.site, claim[1]).full_url())
                                                else:
                                                    url.setTarget(claim[2].url)
                                                if claim[2].iswiki or claim[2].isurl:
                                                    iddata = None
                                                else:
                                                    iddata = pywikibot.Claim(self.site, prop)
                                                    iddata.setTarget(identifier)
                                                if url is None:
                                                    date = None
                                                else:
                                                    date = pywikibot.Claim(self.site, 'P813')
                                                    date.setTarget(self.createdateclaim(min(datetime.datetime.now().strftime('%Y-%m-%d'), datetime.datetime.utcnow().strftime('%Y-%m-%d'))))
                                                if not analyzer.showurl:
                                                    url = None
                                                sourcedata = [source, url, iddata, date]
                                                sourcedata = [sourcepart for sourcepart in sourcedata if sourcepart is not None]
                                                pywikibot.output("Sourcing {}: {}".format(self.label(claim[0]), self.label(claim[1])))
                                                try:
                                                     updatedclaims[claim[0]][self.getlocnumber(claim[1], updatedclaims[claim[0]])].addSources(sourcedata)
                                                except pywikibot.data.api.APIError:
                                                    pass # probably means the sourcing is already there
                                        else:
                                            if claim[0] not in propsdone + propstodo:
                                                propstodo.append(claim[0])
                                            createdclaim = pywikibot.Claim(self.site, claim[0])
                                            if self.QRE.match(claim[1]):
                                                createdclaim.setTarget(pywikibot.ItemPage(self.site, claim[1]))
                                            elif claim[1].startswith("!date!"):
                                                try:
                                                    target = self.createdateclaim(claim[1][6:])
                                                except ValueError as ex:
                                                    print('Unable to analyze date "{}" for {}: {}'.format(claim[1][6:], self.label(claim[0]), ex))
                                                    input('Press enter to continue')
                                                    target = None
                                                if target is None:
                                                    continue
                                                createdclaim.setTarget(target)
                                            elif claim[1].startswith("!q!"):
                                                createdclaim.setTarget(self.createquantityclaim(claim[1][3:].strip()))
                                            elif claim[1].startswith("!i!"):
                                                createdclaim.setTarget(pywikibot.page.FilePage(self.site, claim[1][3:]))
                                            else:
                                                createdclaim.setTarget(claim[1])
                                            pywikibot.output("Adding {}: {}".format(self.label(claim[0]), self.label(claim[1])))
                                            try:
                                                item.addClaim(createdclaim)
                                            except pywikibot.exceptions.OtherPageSaveError as ex:
                                                if claim[1].startswith("!i!"):
                                                    pywikibot.output('Unable to save image {}: {}'.format(claim[1][3:], ex))
                                                    continue
                                                else:
                                                    raise
                                            if claim[0] in updatedclaims:
                                                updatedclaims[claim[0]].append(createdclaim)
                                            else:
                                                updatedclaims[claim[0]] = [createdclaim]
                                            if claim[2]:
                                                if claim[2].dbid:
                                                    if claim[2].iswiki:
                                                        source = pywikibot.Claim(self.site, 'P143')
                                                    else:
                                                        source = pywikibot.Claim(self.site, 'P248')
                                                    source.setTarget(pywikibot.ItemPage(self.site, claim[2].dbid))
                                                else:
                                                    source = None
                                                if claim[2].iswiki:
                                                    url = pywikibot.Claim(self.site, 'P4656')
                                                else:
                                                    url = pywikibot.Claim(self.site, 'P854')
                                                if claim[2].sparqlquery:
                                                    url.setTarget(pywikibot.ItemPage(self.site, claim[1]).full_url())
                                                else:
                                                    url.setTarget(claim[2].url)
                                                if claim[2].iswiki or claim[2].isurl:
                                                    iddata = None
                                                else:
                                                    iddata = pywikibot.Claim(self.site, prop)
                                                    iddata.setTarget(identifier)
                                                if url is None:
                                                    date = None
                                                else:
                                                    date = pywikibot.Claim(self.site, 'P813')
                                                    date.setTarget(self.createdateclaim(min(datetime.datetime.now().strftime('%Y-%m-%d'), datetime.datetime.utcnow().strftime('%Y-%m-%d'))))
                                                if not analyzer.showurl:
                                                    url = None
                                                sourcedata = [source, url, iddata, date]
                                                sourcedata = [sourcepart for sourcepart in sourcedata if sourcepart is not None]
                                                pywikibot.output("Sourcing {}: {}".format(self.label(claim[0]), self.label(claim[1])))
                                                try:
                                                    createdclaim.addSources([s for s in sourcedata if s is not None])
                                                except AttributeError:
                                                    try:
                                                        updatedclaims[claim[0]][self.getlocnumber(claim[1], updatedclaims[claim[0]])].addSources(sourcedata)
                                                    except AttributeError:
                                                        if prop not in propstodo:
                                                            propstodo.append(prop)
                                                        pywikibot.output("Sourcing failed")
                                for (language, description) in analyzer.getdescriptions():
                                    newdescriptions[language].add(description.rstrip('.') if len(description) < 250 else description[:246] + "...")
                                newnames = analyzer.getnames()
                                (newlabels, newaliases) = self.definelabels(labels, aliases, newnames)
                                if newlabels:
                                    item.editLabels(newlabels)
                                if newaliases:
                                    item.editAliases(newaliases)
                                if newlabels or newaliases:
                                    item.get(force=True)
                                    claims = item.claims
                                    claims['Wiki'] = [Quasiclaim(page.title(force_interwiki=True, as_link=True)[2:-2]) for page in item.iterlinks()]
                                    descriptions = item.descriptions
                                    labels = item.labels
                                    aliases = item.aliases
                                if analyzer.longtext():
                                    longtexts.append((analyzer.dbname, analyzer.longtext()))

                                    
            editdescriptions = {}
            for language in newdescriptions.keys():
                newdescription = self.definedescription(language, descriptions.get(language), newdescriptions.get(language))
                if newdescription:
                    editdescriptions[language] = newdescription
            if editdescriptions:
                item.editDescriptions(editdescriptions)
            for prop in unidentifiedprops:
                pywikibot.output("Unknown external {} ({})".format(prop, self.label(prop)))
            if longtexts:
                pywikibot.output('== longtexts ==')
                for longtext in longtexts:
                    pywikibot.output('')
                    pywikibot.output('== {} =='.format(longtext[0]))
                    pywikibot.output(longtext[1])
                    pywikibot.input('(press enter)')
        finally:
            self.savedata()

    def definedescription(self, language, existingdescription, suggestions):
        possibilities = [existingdescription] + list(suggestions)
        pywikibot.output(' ')
        pywikibot.output("Select a description for language {}:".format(language))
        pywikibot.output("Default is to keep the old value (0)")
        for i in range(len(possibilities)):
            if possibilities[i] is None:
                pywikibot.output("{}: No description".format(i))
            else:
                pywikibot.output("{}: {}".format(i, possibilities[i]))
        answer = input("Which one to choose? ")
        try:
            answer = int(answer)
        except ValueError:
            answer = 0
        if answer:
            return possibilities[answer]
        else:
            return None

    def definelabels(self, existinglabels, existingaliases, newnames):
        realnewnames = defaultdict(list)
        anythingfound = False
        for (language, name) in newnames:
            name = name.strip()
            if name.lower() == (existinglabels.get(language) or '').lower() or name.lower() in [n.lower() for n in existingaliases.get(language, [])]:
                continue
            if name not in realnewnames[language] and name not in self.noname:
                realnewnames[language].append(name)
                anythingfound = True
        if anythingfound:
            pywikibot.output(' ')
            pywikibot.output('New names found:')
            for language in realnewnames.keys():
                for name in realnewnames[language]:
                    pywikibot.output('{}: {}'.format(language, name))
            result = input('Add these names? (y/n/[S]elect/x) ')
            if not result or result[0].upper() not in 'YNX':
                chosennewnames = defaultdict(list)
                for language in realnewnames.keys():
                    for name in realnewnames[language]:
                        result = input('{}: {} - '.format(language, name))
                        if (not result) or result[0].upper() == "Y":
                            chosennewnames[language].append(name)
                        elif result[0].upper() == "X":
                            self.noname.append(name)
                realnewnames = chosennewnames
                result = "Y"
            if result[0].upper() == 'X':
                for language in realnewnames.keys():
                    for name in realnewnames[language]:
                        self.noname.append(name)
            elif result[0].upper() != 'N':
                returnvalue = [{}, {}]
                for language in realnewnames.keys():
                    if language in existinglabels.keys():
                        returnvalue[1][language] = existingaliases.get(language, []) + realnewnames[language]
                    else:
                        returnvalue[0][language] = realnewnames[language][0]
                        if len(realnewnames[language]) > 1:
                            returnvalue[1][language] = existingaliases.get(language, []) + realnewnames[language][1:]
                return returnvalue
        return [{}, {}]

    def isclaim(self, value, claim):
        try:
            if value.startswith("!date!"):
                value = value[6:]
            if value.startswith("!q!"):
                value = re.search("\d+(?:\.\d+)?", value).group(0)
            elif value.startswith("!i!"):
                value = value[3:].strip()
            if str(claim.getTarget()) == value:
                return True
            elif claim.type == "wikibase-item" and claim.getTarget().title() == value:
                return True
            elif claim.type == "commonsMedia" and claim.getTarget().title().split(':', 1)[1].replace('_', ' ') == value.replace('_', ' '):
                return True
            elif claim.type == "time" and self.showtime(claim.getTarget()) == self.showtime(self.createdateclaim(value)):
                return True
        except (ValueError, AttributeError):
            return False
            
    def isinclaims(self, value, claims):
        for claim in claims:
            if self.isclaim(value, claim):
                return True
        else:
            return False

    def getlocnumber(self, value, claims):
        for pair in zip(range(len(claims)), claims):
            if self.isclaim(value, pair[1]):
                return pair[0]
        else:
            raise ValueError


class Quasiclaim:
    def __init__(self, title):
        self._target = title

    @property
    def type(self):
        return "external-id"

    def getTarget(self):
        return self._target


    
class Analyzer:
    TAGRE = re.compile("<[^<>]*>")
    SCRIPTRE = re.compile("(?s)<script.*?</script>")
    
    def __init__(self, id, data=None, item=None):
        self.id = id
        self.data = defaultdict(dict) if data is None else data
        self.dbname = None
        self.urlbase = None
        self.urlbase2 = None
        self.urlbase3 = self.urlbase4 = None
        self.showurl = True
        self.dbid = None
        self.dbitem = None
        self.hrtre = None
        self.language = 'en'
        self.escapeunicode = False
        self.escapehtml = False
        self.escapeurl = False
        self.item = item
        self.iswiki = False
        self.sparqlquery = None
        self.isurl = False
        self.skipfirst = False
        self.setup()
        self.site = pywikibot.Site().data_repository()

    def setup(self):
        pass # to be used for putting data into subclasses

    @property
    def url(self):
        usedurl = self.urlbase
        if usedurl is None:
            if not self.sparqlquery:
                pywikibot.output('')
                pywikibot.output("### Skipping {} ({}) ###".format(self.dbname, self.dbproperty))
            return None
        else:
            return usedurl.format(id=encode(self.id))

    @property
    def alturl(self):
        if self.urlbase2:
            return self.urlbase2.format(id=encode(self.id))
        else:
            return None

    @property
    def extraurls(self):
        if self.urlbase3:
            if self.urlbase4:
                return [
                    self.urlbase3.format(id=encode(self.id)),
                    self.urlbase4.format(id=encode(self.id))
                    ]
            else:
                return [self.urlbase3.format(id=encode(self.id))]
        else:
            return []

    def commastrip(self, term):
        term = term.replace("&nbsp;", " ")
        term = term.strip().strip(",").rstrip(".").strip()
        term = term.split("(")[0]
        if "," in term:
            if term.split(',')[1].strip().lower() in ["jr", "sr"]:
                term = term + "."
            else:
                if term.strip()[-1] != term.strip()[-1].lower():
                    term = term.strip() + "."
                term = term.split(",",1)[1] + " " + term.split(",",1)[0]
        while "  " in term:
            term = term.replace("  ", " ")
        term = re.sub("\s*-\s*", "-", term)
        return unescape(term).strip()

    def getdata(self, dtype, text, ask=True):
        text = text.strip().lower().replace("\\n", " ").replace("\n", " ").replace("%20", " ").strip()
        while "  " in text:
            text = text.replace("  ", " ")
        if not text:
            return None
        if dtype in self.data:
            if text in self.data[dtype]:
                if self.data[dtype][text] == "XXX":
                    return None
                else:
                    return self.data[dtype][text]
        if not ask:
            return None
        print("Trying to get a {} out of '{}'".format(dtype, text))
        print("Type Qnnn to let it point to Qnnn from now on, Xnnn to let it point to Qnnn only now, XXX to never use it, or nothing to not use it now")
        answer = input()
        if answer.startswith("Q"):
            self.data[dtype][text] = answer
        elif answer.upper() == "XXX":
            self.data[dtype][text] = "XXX"
            answer = None
        elif answer.startswith("X"):
            answer = "Q" + answer[1:]
        else:
            answer = None
        return answer

    def findclaims(self):
        if not self.id:
            return
        self.html = ''
        if not self.url and not self.sparqlquery:
            return
        newclaims = []
        print()
        pagerequest = None
        if not self.skipfirst:
            try:
                print("Getting {}".format(self.url))
                if "https" in self.url:
                    context = ssl._create_unverified_context()
                    pagerequest = urlopen(self.url, context=context)
                else:
                    pagerequest = urlopen(self.url)
            except (HTTPError, URLError, ConnectionResetError):
                if self.urlbase2:
                    self.urlbase = self.urlbase2
                    print("Getting {}".format(self.url))
                    if "https" in self.url:
                        context = ssl._create_unverified_context()
                        pagerequest = urlopen(self.url, context=context)
                    else:
                        pagerequest = urlopen(self.url)
                else:
                    print("Unable to load {}".format(self.url))
                    return []
            except UnicodeEncodeError:
                print("Unable to receive page {} - not unicode?".format(self.url))
                pagerequest = None
                self.html = ''
        if pagerequest:
            pagebytes = pagerequest.read()
            try:
                self.html = pagebytes.decode('utf-8')
            except UnicodeDecodeError:
                self.html = str(pagebytes)
        for extraurl in self.extraurls:
            try:
                print("Getting {}".format(extraurl))
                if "https" in self.url:
                    context = ssl._create_unverified_context()
                    pagerequest = urlopen(extraurl, context=context)
                else:
                    pagerequest = urlopen(extraurl)
            except (HTTPError, URLError, UnicodeEncodeError):
                print("Unable to receive altpage")
            else:
                pagebytes = pagerequest.read()
                try:
                    self.html = self.html + '\n' + pagebytes.decode('utf-8')
                except UnicodeDecodeError:
                    self.html = self.html + '\n' + str(pagebytes)
        if self.sparqlquery:
            self.html = str(sparql.SparqlQuery().select(self.sparqlquery))
        if not self.html:
            return

        if self.escapeunicode:
            self.html = self.html.encode().decode('unicode-escape')
        if self.escapehtml:
            self.html = unescape(self.html)
        if self.escapeurl:
            self.html = unquote(self.html)
        self.html = self.prepare(self.html)
            
        pywikibot.output("")
        pywikibot.output("=== {} ({}) ====".format(self.dbname, self.dbproperty))
        if self.hrtre:
            match = re.compile("(?s)" + self.hrtre).search(self.html)
            if match:
                text = match.group(1)
                text = text.replace("\\n", "\n")
                text = text.replace("\\t", "\t")
                text = text.replace("\\r", "\n")
                text = text.replace("\r", "\n")
                text = text.replace("\t", " ")
                oldtext = ""
                while oldtext != text:
                    oldtext = text
                    text = self.SCRIPTRE.sub("", text)
                oldtext = ""
                while oldtext != text:
                    oldtext = text
                    text = self.TAGRE.sub(" ", text)
                while "&nbsp;" in text:
                    text = text.replace("&nbsp;", " ")
                while "  " in text:
                    text = text.replace("  ", " ")
                while "\n " in text:
                    text = text.replace("\n ", "\n")
                while "\n\n" in text:
                    text = text.replace("\n\n", "\n")
                text = text.strip()
                pywikibot.output(text)
        pywikibot.output("-" * (len(self.dbname) + 8))
        for (function, prop) in [
                (self.findinstanceof, "P31"),
                (self.findfirstname, "P735"),
                (self.findlastname, "P734"),
                ]:
            result = function(self.html)
            if result:
                newclaims.append((prop, result.strip(), None))
        for (function, prop) in [
                (self.findcountries, "P17"),
                (self.findspouses, "P26"),
                (self.findpartners, "P451"),
                (self.findworkplaces, "P937"),
                (self.findresidences, "P551"),
                (self.findoccupations, "P106"),
                (self.findworkfields, "P101"),
                (self.findpositions, "P39"),
                (self.findtitles, "P97"),
                (self.findemployers, "P108"),
                (self.findranks, 'P410'),
                (self.findschools, "P69"),
                (self.findethnicities, 'P172'),
                (self.findcrimes, 'P1399'),
                (self.findcomposers, "P86"),
                (self.findmoviedirectors, "P57"),
                (self.findscreenwriters, "P58"),
                (self.findproducers, "P162"),
                (self.finddirectorsphotography, "P344"),
                (self.findmovieeditors, "P1040"),
                (self.findproductiondesigners, "P2554"),
                (self.findsounddesigners, "P5028"),
                (self.findcostumedesigners, "P2515"),
                (self.findmakeupartists, "P4805"),
                (self.findarchitects, "P84"),
                (self.findgenres, "P136"),
                (self.findcast, "P161"),
                (self.findmaterials, "P186"),
                (self.findprodcoms, "P272"),
                (self.findoriglanguages, "P364"),
                #(self.findcolors, "P462"),
                (self.findlanguagesspoken, "P1412"),
                (self.findnativelanguages, "P103"),
                (self.findpseudonyms, "P742"),
                (self.findparts, "P527"),
                (self.findpartofs, "P361"),
                (self.findinstruments, "P1303"),
                (self.findlabels, "P264"),
                (self.findsports, "P641"),
                (self.findawards, "P166"),
                (self.findnominations, "P1411"),
                (self.findmemberships, "P463"),
                (self.findsportteams, "P54"),
                (self.findparties, "P102"),
                (self.findbranches, "P241"),
                (self.findconflicts, "P607"),
                (self.findteampositions, 'P413'),
                (self.findpolitical, "P1142"),
                (self.findstudents, "P802"),
                (self.finddocstudents, "P185"),
                (self.findteachers, "P1066"),
                (self.findadvisors, "P184"),
                (self.findinfluences, "P737"),
                (self.finddegrees, "P512"),
                (self.findparticipations, "P1344"),
                (self.findnationalities, "P27"),
                (self.findreligions, "P140"),
                (self.findchildren, "P40"),
                (self.findsiblings, "P3373"),
                (self.findkins, "P1038"),
                (self.findincollections, "P6379"),
                (self.findinworks, "P1441"),
                (self.findmovements, "P135"),
                (self.findorigcountries, "P495"),
                (self.findwebpages, "P973"),
                (self.findsources, "P1343"),
                (self.findchoriginplaces, 'P1321'),
                (self.findpatronof, 'P2925'),
                (self.findnotableworks, 'P800'),
        ]:
            results = function(self.html) or []
            for result in results:
                if result is not None and str(result).strip() and result != self.item:
                    newclaims.append((prop, result, self))
        for (function, prop) in [
                (self.findcountry, "P17"),
                (self.findgender, "P21"),
                (self.findfather, "P22"),
                (self.findmother, "P25"),
                (self.findreligion, "P140"),
                (self.findadminloc, "P131"),
                (self.findlocation, "P276"),
                (self.findformationlocation, "P740"),
                (self.findbirthplace, "P19"),
                (self.finddeathplace, "P20"),
                (self.findmannerdeath, "P1196"),
                (self.findcausedeath, "P509"),
                (self.findburialplace, "P119"),
                (self.findorigcountry, "P495"),
                (self.findnationality, "P27"),
                (self.findethnicity, 'P172'),
                (self.findorientation, 'P91'),
                (self.findaddress, "P969"),
                (self.findhaircolor, "P1884"),
                (self.finduse, "P366"),
                (self.findmountainrange, "P4552"),
                (self.findviaf, "P214"),
                (self.findrelorder, "P611"),
                (self.findtwitter, "P2002"),
                (self.findfacebook, "P2013"),
                (self.findfacebookpage, "P4003"),
                (self.findchoriginplace, 'P1321'),
                (self.findwebsite, 'P856'),
                (self.findvoice, 'P412'),
                (self.findfamily, 'P53'),
                (self.findgens, 'P5025'),
                (self.findchesstitle, 'P2962'),
                (self.findfeastday, 'P841'),
                (self.findbloodtype, 'P1853'),
                ]:
            result = function(self.html)
            if result:
                if prop == 'P856' and 'wikipedia.org' in result:
                    pass
                elif prop in ['P2013', 'P4003'] and result == 'pages':
                    pass
                else:
                    newclaims.append((prop, result.strip(), self))
        for (function, prop) in [
                (self.findbirthdate, "P569"),
                (self.finddeathdate, "P570"),
                (self.findbaptismdate, "P1636"),
                (self.findburialdate, 'P4602'),
                (self.findinception, "P571"),
                (self.finddissolution, "P576"),
                (self.findpubdate, "P577"),
                (self.findfloruit, "P1317"),
                (self.findfloruitstart, "P2031"),
                (self.findfloruitend, ":2032"),
                ]:
            result = function(self.html)
            if result:
                result = result.strip()
                if "?" not in result and re.search("\d{3}", result):
                    newclaims.append((prop, "!date!" + result, self))
        for (function, prop) in [
                (self.findfloorsabove, "P1101"),
                (self.findfloorsbelow, "P1139"),
                ]:
            result = function(self.html)
            if result:
                newclaims.append((prop, str(int(result)), self))
        for (function, prop) in [
                (self.findheights, "P2048"),
                (self.findweights, "P2067"),
                (self.findelevations, "P2044"),
                (self.finddurations, "P2047"),
                (self.findprominences, "P2660"),
                (self.findisolations, "P2659"),
                ]:
            results = function(self.html) or []
            for result in results:
                if result:
                    if result.strip():
                        newclaims.append((prop, "!q!" + result, self))

        for (function, prop) in [
                (self.findimage, 'P18'),
                (self.findcoatarms, 'P94'),
                (self.findsignature, 'P109'),
                ]:
            result = function(self.html)
            if result:
                result = re.sub('(<.*?>)', '', result)
                result = result.split('>')[-1]
                if len(result.strip()) > 2 and '.' in result:
                    newclaims.append((prop, "!i!" + result, None))

        result = self.findisni(self.html)
        if result:
            m = re.search("(\d{4})\s*(\d{4})\s*(\d{4})\s*(\w{4})", result)
            if m:
                newclaims.append(("P213", "{} {} {} {}".format(m.group(1), m.group(2), m.group(3), m.group(4)), self))

        for (prop, result) in self.findmixedrefs(self.html) or []:
            if result is not None:
                result = result.strip()
                if prop in ['P1309', 'P1255']:
                    result = result.replace('vtls', '')
                elif prop == 'P1368':
                    result = result.split('-')[-1]
                elif prop == "P409":
                    result = result.strip().lstrip("0")
                elif prop == 'P396' and '\\' not in result:
                    result = result.replace('%5C', '\\')
                    if '\\' not in result:
                        m = re.match('^(.*?)(\d+)', result)
                        result = 'IT\\ICCU\\{}\\{}'.format(m.group(1), m.group(2))
                if result:
                    newclaims.append((prop, result, self))
   
        print()
        for (function, prop) in [
                (self.findcoords, "coordinates"),
                ]:
            result = function(self.html)
            if result:
                pywikibot.output("Please add yourself: {} - {}".format(prop, result))
        return newclaims

    def prepare(self, html):
        return html

    def singlespace(self, text):
        text = text.replace('\n', ' ')
        while '  ' in text:
            text = text.replace('  ', ' ')
        return text.strip()

    def getdescriptions(self):
        return [(self.language, self.singlespace(unescape(self.TAGRE.sub(' ',x)))) for x in self.finddescriptions(self.html) or [] if x] +\
               [(language, self.singlespace(unescape(self.TAGRE.sub(' ',x)))) for (language, x) in self.findlanguagedescriptions(self.html) or [] if x]

    def longtext(self):
        result = self.TAGRE.sub(' ', self.findlongtext(self.html) or '')
        result = result.replace('\t', '\n').replace('\r', '')
        while '  ' in result:
            result = result.replace('  ', ' ')
        if '\n ' in result:
            result = result.replace('\n ', '\n')
        if ' \n' in result:
            result = result.replace(' \n', '\n')
        while '\n\n' in result:
            result = result.replace('\n\n', '\n')
        return result.strip()

    def findlongtext(self, html):
        return None

    def finddescriptions(self, html):
        return [self.finddescription(html)]

    def findlanguagedescriptions(self, html):
        return None

    def finddescription(self, html):
        return None

    def getlanguage(self, code):
        if not code:
            return self.language
        translation = {
            'cz': 'cs',
            'hbo': 'he',
            'simple': 'en',
            'be-tarask': 'be-x-old',
            'nb': 'no',
            }
        if code in translation.keys():
            return translation[code]
        elif code[-1] in '123456789':
            return self.getlanguage(code[:-1])
        else:
            return code.replace('_', '-')

    def findwikipedianames(self, html):
        links = self.findallbyre('//(\w+\.wikipedia\.org/wiki/[^\'"<>\s]+)', html)
        return [(self.getlanguage(link.split('.')[0]), unescape(unquote(link.split('/')[-1].replace('_', ' '))).split('(')[0]) for link in links]

    def getnames(self):
        return [(self.language, (self.commastrip(term))) for term in self.findnames(self.html) or [] if term and term.strip()] +\
               [(self.getlanguage(language), self.commastrip(term)) for (language, term) in self.findlanguagenames(self.html) or [] if term and term.strip()] +\
               self.findwikipedianames(self.html)

    def findnames(self, html):
        return None

    def findlanguagenames(self, html):
        return None

    def findinstanceof(self, html):
        return None

    def findgender(self, html):
        return None

    def findfather(self, html):
        return None

    def findmother(self, html):
        return None

    def findspouses(self, html):
        return None

    def findpartners(self, html):
        return None

    def findreligion(self, html):
        return None

    def findreligions(self, html):
        return None

    def findchildren(self, html):
        return None

    def findsiblings(self, html):
        return None

    def findkins(self, html):
        return None

    def findcountry(self, html):
        return None

    def findcountries(self, html):
        return None

    def findorigcountry(self, html):
        return None
    
    def findadminloc(self, html):
        return None

    def findlocation(self, html):
        return None

    def findformationlocation(self, html):
        return None

    def findbirthplace(self, html):
        return None

    def finddeathplace(self, html):
        return None

    def findburialplace(self, html):
        return None

    def findmannerdeath(self, html):
        return None

    def findcausedeath(self, html):
        return None

    def findchoriginplace(self, html):
        return None
    
    def findchoriginplaces(self, html):
        return None

    def findworkplaces(self, html):
        return None

    def findresidences(self, html):
        return None

    def findnationality(self, html):
        return None

    def findethnicity(self, html):
        return None

    def findethnicities(self, html):
        return None

    def findorientation(self, html):
        return None

    def findnationalities(self, html):
        return None

    def findfirstname(self, html):
        return None

    def findlastname(self, html):
        return None

    def findaddress(self, html):
        return None

    def findhaircolor(self, html):
        return None

    def findcoords(self, html):
        return None

    def findbirthdate(self, html):
        return None

    def finddeathdate(self, html):
        return None

    def findbaptismdate(self, html):
        return None

    def findburialdate(self, html):
        return None

    def findinception(self, html):
        return None

    def finddissolution(self, html):
        return None

    def findpubdate(self, html):
        return None

    def findfloruit(self, html):
        return None

    def findfloruitstart(self, html):
        return None

    def findfloruitend(self, html):
        return None

    def findheights(self, html):
        return [self.findheight(html)]

    def findheight(self, html):
        return None

    def findweights(self, html):
        return [self.findweight(html)]

    def findweight(self, html):
        return None

    def findoccupations(self, html):
        return None

    def findworkfields(self, html):
        return None
    
    def findpositions(self, html):
        return None

    def findtitles(self, html):
        return None

    def findemployers(self, html):
        return None

    def findranks(self, html):
        return None

    def findschools(self, html):
        return None

    def findcrimes(self, html):
        return None

    def findmoviedirectors(self, html):
        return None

    def findscreenwriters(self, html):
        return None

    def findproducers(self, html):
        return None

    def finddirectorsphotography(self, html):
        return None

    def findmovieeditors(self, html):
        return None

    def findproductiondesigners(self, html):
        return None

    def findsounddesigners(self, html):
        return None

    def findcostumedesigners(self, html):
        return None

    def findmakeupartists(self, html):
        return None
    
    def findcomposers(self, html):
        return None

    def findarchitects(self, html):
        return None

    def findgenres(self, html):
        return None

    def findcast(self, html):
        return None

    def findmaterials(self, html):
        return None

    def findprodcoms(self, html):
        return None

    def findoriglanguages(self, html):
        return None

    def finddurations(self, html):
        return None

    def findprominences(self, html):
        return None

    def findisolations(self, html):
        return None

    def findlanguagesspoken(self, html):
        return None

    def findnativelanguages(self, html):
        return None

    def findcolors(self, html):
        return None

    def finduse(self, html):
        return None

    def findfloorsabove(self, html):
        return None

    def findfloorsbelow(self, html):
        return None

    def findelevations(self, html):
        return None

    def findmountainrange(self, html):
        return None

    def findrelorder(self, html):
        return None

    def findwebsite(self, html):
        return None

    def findwebpages(self, html):
        return None

    def findsources(self, html):
        return None

    def findvoice(self, html):
        return None

    def findfamily(self, html):
        return None

    def findgens(self, html):
        return None

    def findpseudonyms(self, html):
        return None

    def findparts(self, html):
        return None

    def findpartofs(self, html):
        return None

    def findinstruments(self, html):
        return None

    def findlabels(self, html):
        return None

    def findsports(self, html):
        return None

    def findawards(self, html):
        return None

    def findnominations(self, html):
        return None

    def findmemberships(self, html):
        return None

    def findsportteams(self, html):
        return None

    def findparties(self, html):
        return None

    def findbranches(self, html):
        return None

    def findconflicts(self, html):
        return None
    
    def findteampositions(self, html):
        return None

    def findpolitical(self, html):
        return None

    def findstudents(self, html):
        return None

    def finddocstudents(self, html):
        return None

    def findteachers(self, html):
        return None

    def findadvisors(self, html):
        return None

    def findinfluences(self, html):
        return None

    def finddegrees(self, html):
        return None

    def findparticipations(self, html):
        return None

    def findviaf(self, html):
        return None

    def findisni(self, html):
        return None

    def findtwitter(self, html):
        return None

    def findfacebook(self, html):
        return None

    def findfacebookpage(self, html):
        return None

    def findincollections(self, html):
        return None

    def findinworks(self, html):
        return None

    def findmovements(self, html):
        return None

    def findorigcountries(self, html):
        return None

    def findchesstitle(self, html):
        return None

    def findfeastday(self, html):
        return None

    def findbloodtype(self, html):
        return None

    def findpatronof(self, html):
        return None

    def findnotableworks(self, html):
        return None

    def findimage(self, html):
        return None

    def findcoatarms(self, html):
        return None

    def findsignature(self, html):
        return None

    def findmixedrefs(self, html):
        return None

    def finddefaultmixedrefs(self, html, includesocial=True):
        defaultmixedrefs = [
            ("P214", self.findbyre('viaf.org/(?:viaf/)?(\d+)', html)),
            ("P227", self.findbyre('d-nb\.info/(?:gnd/)?([\d\-xX]+)', html)),
            ("P244", self.findbyre('id\.loc\.gov/authorities/\w+/(\w+)', html)),
            ("P244", self.findbyre('https?://lccn\.loc\.gov/(\w+)', html)),
            ("P245", self.findbyre('https?://www.getty.edu/[^"\'\s]+subjectid=(\w+)', html)),
            ("P245", self.findbyre('getty.edu/page/ulan/(\w+)', html)),
            ("P268", self.findbyre('https?://catalogue.bnf.fr/ark./\d+/(?:cb)?(\w+)', html)),
            ("P268", self.findbyre('data\.bnf\.fr/ark:/\d+/cb(\w+)', html)),
            ("P269", self.findbyre('https?://\w+.idref.fr/(\w+)', html)),
            ("P345", self.findbyre('https?://www.imdb.com/\w+/(\w+)', html)),
            ("P349", self.findbyre('https?://id.ndl.go.jp/auth/[^"\'\s]+/(\w+)', html)),
            ("P396", self.findbyre('opac\.sbn\.it/opacsbn/opac/[^<>\'"\s]+\?bid=([^\s\'"<>]+)', html)),
            ("P409", self.findbyre('https?://nla.gov.au/anbd.aut-an(\w+)', html)),
            ("P434", self.findbyre('https?://musicbrainz.org/\w+/([\w\-]+)', html)),
            ("P496", self.findbyre('https?://orcid.org/([\d\-]+)', html)),
            ("P535", self.findbyre('https?://www.findagrave.com/memorial/(\w+)', html)),
            ("P535", self.findbyre('https?://www.findagrave.com/cgi-bin/fg.cgi\?[^<>"\']*id=(\w+)', html)),
            ("P549", self.findbyre('genealogy.math.ndsu.nodak.edu/id.php\?id=(\w+)', html)),
            ("P650", self.findbyre('https?://rkd.nl(?:/\w+)?/explore/artists/(\w+)', html)),
            ("P651", self.findbyre('biografischportaal\.nl/persoon/(\w+)', html)),
            ("P723", self.findbyre('dbnl\.(?:nl|org)/auteurs/auteur.php\?id=(\w+)', html)),
            ("P866", self.findbyre('perlentaucher.de/autor/([\w\-]+)', html)),
            ("P902", self.findbyre('hls-dhs-dss.ch/textes/\w/[A-Z]?(\d+)\.php', html)),
            ("P906", self.findbyre('libris.kb.se/(?:resource/)?auth/(\w+)', html)),
            ("P950", self.findbyre('catalogo.bne.es/[^"\'\s]+authority.id=(\w+)', html)),
            ("P1220", self.findbyre('//ibdb.com/person.php\?id=(\d+)', html)),
            ('P1233', self.findbyre('https?://www.isfdb.org/cgi-bin/ea.cgi\?(\d+)', html)),
            ('P1417', self.findbyre('https://www.britannica.com/([\w\-/]+)', html)),
            ("P1422", self.findbyre('ta.sandrartnet/-person-(\w+)', html)),
            ("P1563", self.findbyre('https?://www-history.mcs.st-andrews.ac.uk/Biographies/([^\'"<>\s]+)', html)),
            ("P1728", self.findbyre('https?://www.allmusic.com/artist/([\w\-]+)', html)),
            ("P1749", self.findbyre('https?://www.parlement(?:airdocumentatiecentrum)?.(?:com|nl)/id/(\w+)', html)),
            ("P1788", self.findbyre('huygens.knaw.nl/vrouwenlexicon/lemmata/data/([^"\'<>\s]+)', html)),
            ("P1802", self.findbyre('https?://emlo.bodleian.ox.ac.uk/profile/person/([\w\-]+)', html)),
            ("P1842", self.findbyre('https?://gameo.org/index.php\?title=([^\'"\s]+)', html)),
            ("P1871", self.findbyre('https?://(?:data|thesaurus).cerl.org/(?:thesaurus|record)/(\w+)', html)),
            ("P1871", self.findbyre('thesaurus.cerl.org/cgi-bin/record.pl\?rid=(\w+)', html)),
            ("P1902", self.findbyre('https?://open.spotify.com/artist/(\w+)', html)),
            ("P1907", self.findbyre('https?://adb.anu.edu.au/biography/([\w\-]+)', html)),
            ('P1938', self.findbyre('https?://www.gutenberg.org/ebooks/author/(\d+)', html)),
            ("P1953", self.findbyre('https?://www.discogs.com/artist/([\w\+]+)', html)),
            ("P2016", self.findbyre('hoogleraren\.ub\.rug\.nl/hoogleraren/(\w+)', html)),
            ('P2038', self.findbyre('https?://www.researchgate.net/profile/([^\'"<>\s\?]+)', html)),
            ("P2163", self.findbyre('id\.worldcat\.org/fast/(\d+)', html)),
            ("P2332", self.findbyre('/arthistorians\.info/(\w+)', html)),
            ("P2373", self.findbyre('https?://genius.com/artists/([^\s\'"]*)', html)),
            ("P2397", self.findbyre('youtube\.com/channel/([\w\-_]+)', html)),
            ("P2454", self.findbyre('https?://www.dwc.knaw.nl/[^\'"\s]+=(\w+)', html)),
            ("P2456", self.findbyre('https?://dblp.uni-trier.de/pid/([\w/]+)', html)),
            ("P2469", self.findbyre('theatricalia.com/person/(\w+)', html)),
            ("P2722", self.findbyre('deezer.com/artist/(\w+)', html)),
            ("P2909", self.findbyre('https?://www.secondhandsongs.com/artist/(\w+)', html)),
            ("P2941", self.findbyre('munksroll.rcplondon.ac.uk/Biography/Details/(\d+)', html)),
            ("P2949", self.findbyre('www\.wikitree\.com/wiki/(\w+-\d+)', html)),
            ("P2963", self.findbyre('goodreads\.com/author/show/(\d+)', html)),
            ("P2969", self.findbyre('goodreads\.com/book/show/(\d+)', html)),
            ("P3040", self.findbyre('https?://soundcloud.com/([\w\-]+)', html)),
            ("P3192", self.findbyre('https?://www.last.fm/music/([^\'"\s]+)', html)),
            ("P3241", self.findbyre('https?://www.newadvent.org/cathen/(\w+)\.htm', html)),
            ("P3265", self.findbyre('https?://myspace.com/([\w\-_/]+)', html)),
            ("P3368", self.findbyre('https?://prabook.com/web/[^/<>"\']+/(\d+)', html)),
            ("P3368", self.findbyre('prabook.com/web/person-view.html\?profileId=(\d+)', html)),
            ("P3518", self.findbyre('play.google.com/store/music/artist\?id=(\w+)', html)),
            ("P3435", self.findbyre('vgmdb\.net/artist/(\w+)', html)),
            ("P3478", self.findbyre('songkick\.com/artists/(\w+)', html)),
            ("P3630", self.findbyre('https?://www.babelio.com/auteur/[^<>\'"\s]+/(\d+)', html)),
            ("P3854", self.findbyre('soundtrackcollector.com/\w+/(\w+)', html)),
            ("P4013", self.findbyre('https?://giphy.com/(\w+)', html)),
            ("P4073", self.findbyre('(\w+)\.wikia\.com', html)),
            ("P4198", self.findbyre('https?://play.google.com/store/music/artist\?id=(\w+)', html)),
            ("P4228", self.findbyre('www.eoas.info/biogs/([^\s]+)\.html', html)),
            ("P4228", self.findbyre('www.eoas.info%2Fbiogs%2F([^\s]+)\.html', html)),
            ("P4252", self.findbyre('www.mathnet.ru/[\w/\.]+\?.*?personid=(\w+)', html)),
            ("P4862", self.findbyre('https?://www.amazon.com/[\w\-]*/e/(\w+)', html)),
            ("P5357", self.findbyre('sf-encyclopedia.com/entry/([\w_]+)', html)),
            ("P5404", self.findbyre('rateyourmusic.com/artist/([^\'"<>\s]+)', html)),
            ("P5570", self.findbyre('www.noosfere.org/[\w\./]+\?numauteur=(\w+)', html)),
            ("P5882", self.findbyre('www\.muziekweb\.nl/\w+/(\w+)', html)),
            ("P5924", self.findbyre('lyrics.wikia.com/wiki/([^\'"<>\s]*)', html)),
            ("P6194", self.findbyre('biographien\.ac.\at/oebl/oebl_\w/[^\s\.]+\.', html)),
            ("P6517", self.findbyre('whosampled.com/([^\'"<>/\s]+)', html)),
            ("P7032", self.findbyre('historici.nl/Onderzoek/Projecten/Repertorium/app/personen/(\d+)', html)),
            ("P7032", self.findbyre('repertoriumambtsdragersambtenaren1428-1861/app/personen/(\d+)', html)),
            ("P7545", self.findbyre('https?://www.askart.com/artist/[\w_]*/(\d+)/', html)),
            ]
        if includesocial:
            defaultmixedrefs += [
                ("P2002", self.findbyre('https?://(?:www\.)?twitter.com/#?(\w+)', html)),
                ("P2003", self.findbyre('https?://(?:\w+\.)?instagram.com/([^/\s\'"]{2,})', html)),
                ("P2013", self.findbyre('https?://www.facebook.com/([^/\s\'"<>\?]+)', html)),
                ("P2847", self.findbyre('https?://plus.google.com/(\+?\w+)', html)),
                ("P2850", self.findbyre('https?://itunes.apple.com/(?:\w+/)?artist/(?:\w*/)?[a-z]{0,2}(\d{3,})', html)),
                ("P3258", self.findbyre('https?://(\w+)\.livejournal.com', html)),
                ("P3258", self.findbyre('https?://users\.livejournal.com/(\w+)', html)),
                ("P3283", self.findbyre('https?://([^/"\']+)\.bandcamp.com', html)),
                ("P4003", self.findbyre('https?://www.facebook.com/pages/([^\s\'"<>]+)', html)),
                ("P4175", self.findbyre('https://www.patreon.com/([\w\-]+)', html)),
                ("P6634", self.findbyre('\.linkedin\.com/in/([\w\-]+)', html)),
            ]
        result = [pair for pair in defaultmixedrefs if pair[0] != self.dbproperty]
        commonsresult = self.findbyre('commons\.wikimedia\.org/wiki/\w+:([^\'"<>\s]+)', html)
        if commonsresult:
            result += [("P18", "!i!" + commonsresult)]
        return [r for r in result if r[1] and
                not (r[0] == 'P2013' and r[1].startswith('pages')) and
                not (r[0] == 'P2013' and r[1] == 'plugins') and
                not (r[0] == 'P214' and r[1].lower() == 'sourceid') and
                not (r[0] == 'P3258' and r[1].lower() in ['users', 'comunity', 'www']) and
                not r[1].lower() == 'search']


    def findbyre(self, regex, html, dtype=None, skips=None, alt=None):
        if not skips: skips = []
        if not alt: alt = []
        m = re.search(regex, html)
        if m:
            for alttype in alt:
                if self.getdata(alttype, m.group(1), ask=False) and self.getdata(alttype, m.group(1), ask=False) != 'XXX':
                    return self.getdata(alttype, m.group(1), ask=False)
            for skip in skips:
                if self.getdata(skip, m.group(1), ask=False) and self.getdata(skip, m.group(1), ask=False) != 'XXX':
                    return None
            if dtype:
                return self.getdata(dtype, m.group(1))
            else:
                return m.group(1)
        else:
            return None

    def findallbyre(self, regex, html, dtype=None, skips=None, alt=None):
        if not skips: skips = []
        if not alt: alt = []
        matches = re.findall(regex, html)
        result = set()
        for match in matches:
            doskip = False
            for alttype in alt:
                if self.getdata(alttype, match, ask=False) and self.getdata(alttype, match, ask=False) != 'XXX':
                    result.add(self.getdata(alttype, match, ask=False))
                    doskip = True
            for skip in skips:
                if self.getdata(skip, match, ask=False) and self.getdata(skip, match, ask=False) != 'XXX':
                    doskip = True
            if doskip: continue
            if dtype:
                newresult = self.getdata(dtype, match)
                if newresult: result.add(newresult)
            else:
                result.add(match)
        return list(result)

class IsniAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P213"
        self.dbid = "Q423048"
        self.dbname = "International Standard Name Identifier"
        self.id = self.id.replace(' ', '')
        self.id = self.id[:4] + '+' + self.id[4:8] + '+' + self.id[8:12] + '+' + self.id[12:]
        self.urlbase = 'http://www.isni.org/{id}'
        self.hrtre = '(<span class="rec.mat.long">.*?</span>)Sources'
        self.isperson = False
        self.language = 'en'

    @property
    def url(self):
        return "http://www.isni.org/{id}".format(id=self.id).replace(" ", "")

    def findlanguagenames(self, html):
        section = self.findbyre('(?s)>Name</td></tr>(.*?)</tr>', html)
        if section:
            return [('en', name) for name in self.findallbyre('(?s)<span>(.*?)(?:\([^\{\}<>]*\))?\s*</span>', section)]

    def finddescriptions(self, html):
        section = self.findbyre('(?s)>Name</td></tr>(.*?)</tr>', html)
        if section:
            return self.findallbyre('(?s)\(([^<>]*?)\)', section)

    def findinstanceof(self, html):
        result = self.findbyre('<span class="rec.mat.long"><img alt="(.*?)"', html, 'instanceof')
        self.isperson = result == "Q5"
        return result

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html)

    def findoccupations(self, html):
        section = self.findbyre('(?s) role:.*?(<td.*?</tr>)', html)
        if section:
            return section.findallbyre('(?s)<span>(.*?)<', html, 'occupation')
        
    def findbirthdate(self, html):
        return self.findbyre('born\s+([\w\-]*\d{4}[\w\-]*)', html)

    def finddeathdate(self, html):
        return self.findbyre('deceased\s+([\w\-]*\d{4}[\w\-]*)', html)
        
class ViafAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P214"
        self.dbid = "Q54919"
        self.dbname = "Virtual International Authority File"
        self.urlbase = "https://viaf.org/viaf/{id}/"
        self.hrtre = '(<ns1:Document.*?)<ns1:history>'
        self.language = 'en'
        self.escapehtml = True
        self.sourcelanguage = {
            'DNB': 'de',
            'LC': 'en',
            'JPG': 'en',
            'SUDOC': 'fr',
            'NDL': 'ja',
            'NLA': 'en',
            'NKC': 'cs',
            'SELIBR': 'sv',
            'NLI': 'he',
            'BNE': 'es',
            'PTBNP': 'pt',
            'NTA': 'nl',
            'BIBSYS': 'nb',
            'BAV': 'en',
            'NUKAT': 'pl',
            'BNC': 'ca',
            'EGAXA': 'en',
            'LNB': 'lv',
            'NSK': 'hr',
            'LAC': 'en',
            'NLP': 'pl',
            'BNCHL': 'es',
            'N6I': 'en',
            'FAST': 'en',
            'RERO': 'fr',
            'B2Q': 'fr',
            'DBC': 'da',
            'BLBNB': 'pt',
            'KRNLK': 'ko',
            'ISNI': 'en',
            'BNF': 'fr',
            'DE663': 'de',
            'WKP': 'en',
            'VLACC': 'nl',
            'ERRR': 'et',
            'NII': 'ja',
            'BNL': 'fr',
            'SWNL': 'fr',
            'NLR': 'ru',
            'ICCU': 'it',
            'LNL': 'ar',
            'W2Z': 'nb',
            'LIH': 'lt',
            'UIY': 'is',
            'CAOONL': 'en',
            'SIMACOB': 'sl',
            'CYT': 'zh',
            'SZ': 'de',
            'PLWABN': 'pl',
            'NLB': 'en',
            'SKMASNL': 'sk',
            'ARBABN': 'es',
            'J9U': 'he',
            }
            
    def getid(self, name, html):
        result = self.findbyre('>{}\|([^<>]+)'.format(name), html)
        if result:
            return result.replace(" ", "")

    def findlanguagenames(self, html):
        languagenames = set()
        for section in self.findallbyre('(?s)<ns1:x\d+>(.*?)</ns1:x\d+>', html):
            for name in self.findallbyre('<ns1:subfield code="a">(.*?)<', section):
                for source in self.findallbyre('<ns1:s>(.*?)<', section):
                    languagenames.add((self.sourcelanguage[source], name))
        names = [name[1] for name in languagenames]
        for name in self.findallbyre('<ns1:subfield code="a">(.*?)<', html):
            if name not in names:
                languagenames.add(('en', name))
        return languagenames
                
    def findlanguagedescriptions(self, html):
        result = set()
        for section in self.findallbyre('(?s)<ns1:x\d+>(.*?)</ns1:x\d+>', html):
            for name in self.findallbyre('<ns1:subfield code="c">(.*?)<', section):
                for source in self.findallbyre('<ns1:s>(.*?)<', section):
                    result.add((self.sourcelanguage[source], name))
        names = [name[1] for name in result]
        for name in self.findallbyre('<ns1:subfield code="c">(.*?)<', html):
            if name not in names:
                result.add(('en', name))
        return result
    
    def findgender(self, html):
        return self.findbyre('<ns1:gender>([^<>]+)</ns1:gender>', html, 'gender')

    def findnationalities(self, html):
        section = self.findbyre('<ns1:nationalityOfEntity>(.*?)</ns1:nationalityOfEntity>', html)
        if section:
            return self.findallbyre('<ns1:text>([^<>]+)</ns1:text>', section, 'country')

    def findlanguagesspoken(self, html):
        section = self.findbyre('<ns1:languageOfEntity>(.*?)</ns1:languageOfEntity>', html)
        if section:
            return self.findallbyre('<ns1:text>([^<>]+)</ns1:text>', section, 'language')

    def findoccupations(self, html):
        sections = self.findallbyre('<ns1:occupation>(.*?)</ns1:occupation>', html)
        section = '\n'.join(sections)
        return self.findallbyre('<ns1:text>(.*?)</ns1:text>', section, 'occupation')

    def findworkfields(self, html):
        sections = self.findallbyre('<ns1:fieldOfActivity>(.*?)</ns1:fieldOfActivity>', html)
        section = '\n'.join(sections)
        return self.findallbyre('<ns1:text>(.*?)</ns1:text>', section, 'subject')
    
    def findmixedrefs(self, html):
        result = [
            ("P214", self.findbyre('<ns0:directto>(\d+)<', html)),
            ("P227", self.getid("DNB", html)),
            ("P244", self.getid("LC", html)),
            ("P245", self.getid("JPG", html)),
            ("P269", self.getid("SUDOC", html)),
            ("P271", self.getid("NII", html)),
            ("P349", self.getid("NDL", html)),
            ("P396", self.getid("ICCU", html)),
            ("P409", self.getid("NLA", html)),
            ('P691', self.getid('NKC', html)),
            ("P906", self.getid("SELIBR", html)),
            ("P949", self.getid("NLI", html)),
            ("P950", self.getid("BNE", html)),
            ("P1005", self.getid("PTBNP", html)),
            ("P1006", self.getid("NTA", html)),
            ("P1015", self.getid("BIBSYS", html)),
            ('P1017', self.getid('BAV', html)),
            ("P1207", self.getid("NUKAT", html)),
            ('P1255', self.getid("SWNL", html)),
            ("P1273", self.getid("BNC", html)),
            ('P1309', self.getid('EGAXA', html)),
            ('P1368', self.getid('LNB', html)),
            ("P1375", self.getid("NSK", html)),
            ("P1670", self.getid("LAC", html)),
            ("P1695", (self.getid("NLP", html) or "").upper() or None),
            #("P1946", self.getid("N6I", html)), #obsolete
            ("P2163", self.getid("FAST", html)),
            #("P3065", self.getid("RERO", html)),
            ("P3280", self.getid("B2Q", html)),
            ("P3846", self.getid("DBC", html)),
            ("P4619", self.getid("BLBNB", html)),
            ("P5034", self.getid("KRNLK", html)),
            ("P5504", self.getid("DE663", html)),
            ("P7369", (self.getid('BNCHL', html) or "")[-9:] or None),
            ("P268", self.findbyre('"http://catalogue.bnf.fr/ark:/\d+/cb(\w+)"', html)),
            ("P1566", self.findbyre('"http://www.geonames.org/(\w+)"', html)),
            ]
        iccu = self.getid("ICCU", html)
        if iccu:
            result += [("P396", "IT\ICCU\{}\{}".format(iccu[:4], iccu[4:]))]
        result += self.finddefaultmixedrefs(html)
        return result

    def findisni(self, html):
        return self.getid("ISNI", html)

    def findnotableworks(self, html):
        works = self.findallbyre('<ns1:work>(.*?)</ns1:work>', html)
        works = [(len(re.findall('(<ns1:s>)', work)), work) for work in works]
        works.sort(reverse=True)
        works = works[:5]
        works = [work for work in works if work[0] > 2]
        return [self.findbyre('<ns1:title>(.*?)<', work[1], 'work') for work in works]
    

class GndAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P227"
        self.dbid = "Q36578"
        self.dbname = "Gemeinsame Normdatei"
        self.urlbase = "https://portal.dnb.de/opac.htm?method=simpleSearch&cqlMode=true&query=nid%3D{id}"
        self.hrtre = '(<table id="fullRecordTable".*?/table>)'
        self.language = 'de'
        self.escapehtml = True

    def finddescriptions(self, html):
        return [
            self.findbyre('(?s)<strong>Weitere Angaben</strong>.*?<td[^<>]*>(.*?)</td>', html),
            self.findbyre('(?s)<strong>Systematik</strong>.*?<td[^<>]*>\s*[^\s]+(.*?)</td>', html),
            self.findbyre('(?s)<strong>Beruf\(e\)</strong>.*?<td[^<>]*>(.*?)</td>', html),
            ]

    def findlongtext(self, html):
        return re.sub('\s', ' ', self.findbyre('(?s)(<table id="fullRecordTable" .*?</table>)', html) or '').replace('<tr>', '\n')

    def findnames(self, html):
        result = []
        section = self.findbyre('(?s)<strong>Sachbegriff</strong>.*?(<td.*?>(.*?)</td>)', html)
        if section:
            result += self.findallbyre('>([^<>\(]*)', section)
        section = self.findbyre('(?s)<strong>Person</strong>.*?(<td.*?>(.*?)</td>)', html)
        if section:
            result += self.findallbyre('>([^<>\(]*)', section)
        section = self.findbyre('(?s)<strong>Synonyme</strong>.*?(<td.*?>(.*?)</td>)', html)
        if section:
            result += self.findallbyre('>([^<>\(]*)', section)
        section = self.findbyre('(?s)<strong>Andere Namen</strong>.*?(<td.*?>(.*?)</td>)', html)
        if section:
            result += self.findallbyre('>([^<>\(]*)', section)
        return result
        
    def findinstanceof(self, html):
        result = self.findbyre('(?s)<strong>Typ</strong>.*?<td.*?>(.*?)(?:\(|</)', html, 'instanceof')
        if not result and '<strong>Person</strong>' in html:
            result = "Q5"
        self.isperson = result == "Q5"
        return result

    def findbirthdate(self, html):
        return self.findbyre('(?s)Lebensdaten:([^<>]*?)-', html)

    def finddeathdate(self, html):
        return self.findbyre('(?s)Lebensdaten:[^<>]*?-([^<>\(\)]*)', html)
        
    def findnationalities(self, html):
        if self.isperson:
            section = self.findbyre('(?s)<strong>Land</strong>.*?<td.*?>(.*?)</td>', html)
            if section:
                return self.findallbyre('([\w\s]+)\(', section, 'country')

    def findcountries(self, html):
        if not self.isperson:
            section = self.findbyre('(?s)<strong>Land</strong>.*?<td.*?>(.*?)</td>', html)
            if section:
                return self.findallbyre('([\w\s]+)\(', section, 'country')

    def findbirthplace(self, html):
        return self.findbyre('(?s)Geburtsort:\s*(?:<[^<>]*>)?([^<>&]*)', html, 'city')
    
    def finddeathplace(self, html): 
        return self.findbyre('(?s)Sterbeort:\s*(?:<[^<>]*>)?([^<>&]*)', html, 'city')

    def findworkplaces(self, html):
        return self.findallbyre('(?s)Wirkungsort:\s*(?:<[^<>]*>)?([^<>]*)\(\d{3}', html, 'city') or\
               self.findallbyre('(?s)Wirkungsort:\s*(?:<[^<>]*>)?([^<>]*)', html, 'city')

    def findoccupations(self, html):
        result = []
        sectionfound = False
        for sectionname in ['Beruf\(e\)', 'Funktion\(en\)', 'Weitere Angaben']:
            if sectionname == 'Weitere Angaben' and sectionfound:
                continue
            section = self.findbyre('(?s)<strong>%s</strong>(.*?)</tr>'%sectionname, html)
            if section:
                sectionfound = True
                result += self.findallbyre('(?s)[>;,]([^<>;,]*)', section, 'occupation')
        return result

    def findgender(self, html):
        return self.findbyre('(?s)<strong>Geschlecht</strong>.*?>([^<>]+)</td', html, 'gender')

    def findinstruments(self, html):
        section = self.findbyre('(?s)<strong>Instrumente.*?<td[^<>]*>(.*?)</td>', html)
        if section:
            section = re.sub('(?s)(\([^\(\)]*\))', ';', section)
            return self.findallbyre('(?s)([\s\w]+)', section, 'instrument')

    def findvoice(self, html):
        section = self.findbyre('(?s)<strong>Instrumente.*?<td[^<>]*>(.*?)</td>', html)
        if section:
            if "(" in section:
                return self.findbyre('(?s)([\s\w]+)\(', section, 'voice')
            else:
                return self.findbyre('(?s)([\s\w]+)', section, 'voice')

    def findlanguagesspoken(self, html):
        if self.isperson:
            section = self.findbyre('(?s)<strong>Sprache.*?<td[^<>]*>(.*?)</td>', html)
            if section:
                return self.findallbyre('([^\{\});]*)\(', section, 'language')

    def finddegrees(self, html):
        section = self.findbyre('(?s)Akademischer Grad.*?<td[^<>]*>(.*?)</td>', html)
        if section:
            return self.findallbyre('([^<>]+)', section, 'degree')

    def findsiblings(self, html):
        section = self.findbyre('(?s)<strong>Beziehungen zu Personen</strong>.*?(<td.*?</td>)', html)
        if section:
            return self.findallbyre('(?s)([^<>]*)(?:</a> )?\((?:Bruder|Schwester)\)', section, 'person')

    def findspouses(self, html):
        section = self.findbyre('(?s)<strong>Beziehungen zu Personen</strong>.*?(<td.*?</td>)', html)
        if section:
            return self.findallbyre('(?s)([^<>]*)(?:</a> )?\((?:Ehemann|Ehefrau)\)', section, 'person')

    def findchildren(self, html):
        section = self.findbyre('(?s)<strong>Beziehungen zu Personen</strong>.*?(<td.*?</td>)', html)
        if section:
            return self.findallbyre('(?s)([^<>]*)(?:</a> )?\((?:Sohn|Tochter)\)', section, 'person')

    def findfather(self, html):
        section = self.findbyre('(?s)<strong>Beziehungen zu Personen</strong>.*?(<td.*?</td>)', html)
        if section:
            return self.findbyre('(?s)([^<>]*)(?:</a> )?\(Vater\)', section, 'person')

    def findmother(self, html):
        section = self.findbyre('(?s)<strong>Beziehungen zu Personen</strong>.*?(<td.*?</td>)', html)
        if section:
            return self.findbyre('(?s)([^<>]*)(?:</a> )?\(Mutter\)', section, 'person')

    def findpseudonyms(self, html):
        section = self.findbyre('(?s)<strong>Beziehungen zu Personen</strong>.*?(<td.*?</td>)', html)
        if section:
            return [self.findbyre('Pseudonym: <a[^<>]*>(.*?)<', section)]
   
    def findwebsite(self, html):
        return self.findbyre('Homepage[^<>]*<a[^<>]*href="(.*?)"', html)

    def findwebpages(self, html):
        return self.findallbyre('Internet[^<>]*<a[^<>]*href="(.*?)"', html)

    def findworkfields(self, html):
        section = self.findbyre('(?s)<strong>Thematischer Bezug</strong>.*?(<td.*?</td>)', html)
        if section:
            result = []
            subjects = self.findallbyre('>([^<>]*)<', section)
            for subject in subjects:
                if ':' in subject:
                    result += self.findallbyre('([\w\s]+)', subject[subject.find(':')+1:], 'subject')
                else:
                    result += self.findallbyre('(.+)', subject, 'subject')
            return result

    def findemployers(self, html):
        section = self.findbyre('(?s)<strong>Beziehungen zu Organisationen</strong>.*?(<td.*?</td>)', html)
        if section:
            return self.findallbyre('(?s)>([^<>]*)<', section, 'employer', alt=['university'])
        else:
            return self.findallbyre('Tätig an (?:d\w\w )?([^<>]*)', html, 'employer', alt=['university'])

    def findsources(self, html):
        section = self.findbyre('(?s)<strong>Quelle</strong>.*?<td[^<>]*(>.*?<)/td>', html)
        if section:
            subsections = self.findallbyre('>([^<>]*)<', section)
            result = []
            for subsection in subsections:
                result += self.findallbyre('([^;]+)', subsection, 'source')
            return result

    def findmemberships(self, html):
        section = self.findbyre('(?s)<strong>Beziehungen zu Organisationen</strong>.*?(<td.*?</td>)', html)
        if section:
            return self.findallbyre('>([^<>]*)</a>', section, 'organization', skips=['religious order', 'employer'])       

    def findrelorder(self, html):
        section = self.findbyre('(?s)<strong>Beziehungen zu Organisationen</strong>.*?(<td.*?</td>)', html)
        if section:
            return self.findbyre('>([^<>]*)</a>', section, 'religious order', skips=['organization', 'employer'])

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html)

    
class LcAuthAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P244"
        self.dbid = "Q13219454"
        self.dbname = "Library of Congress Authorities"
        #self.urlbase = None
        self.hrtre = '(<h1.*?)<h3>(?:Editorial Notes|Change Notes|Sources|Alternate Formats)'
        self.language = 'en'
        self.escapehtml = True

    @property
    def url(self):
        if self.isperson:
            return "http://id.loc.gov/authorities/names/{id}.html".format(id=self.id)
        elif self.id.startswith("s"):
            return "http://id.loc.gov/authorities/subjects/{id}.html".format(id=self.id)
        
    @property
    def isperson(self):
        return self.id.startswith("n")

    def findinstanceof(self, html):
        if self.isperson:
            return 'Q5'

    def findnames(self, html):
        section = self.findbyre('(?s)<h3>Variants</h3><ul[^<>]*>(.*?)</ul>', html)
        if section:
            result = self.findallbyre('>([^<>]*)?(?:,[\s\d\-]+)<', section)
        else:
            result = []
        return result +\
               self.findallbyre('skos:prefLabel">(.*?)(?:</|, \d)', html) +\
               self.findallbyre('skosxl:literalForm">(.*?)(?:<|, \d)', html)

    def finddescriptions(self, html):
        result = [self.findbyre('<title>([^<>]*)-', html)]
        section = self.findbyre('(?s)<h3>Sources</h3>(.*?)</ul>', html)
        if section:
            result += self.findallbyre('\(([^<>]*?)\)', section)
        return result

    def findlongtext(self, html):
        return self.findbyre('(?s)<h3>Sources</h3>(.*?)</ul>', html)

    def findfirstname(self, html):
        if self.isperson:
            return self.findbyre('<h1[^<>]*>[^<>]*?,\s*(\w*)', html, 'firstname')

    def findlastname(self, html):
        if self.isperson:
            return self.findbyre('h1[^<>]*>([^<>]*?),', html, 'lastname')

    def findinstanceof(self, html):
        return self.findbyre('MADS/RDF ([^<>]+)', html, 'instanceof')

    def findbirthdate(self, html):
        result = self.findbyre('<li><h3>Birth Date</h3><ul[^<>]*>(\d{8})<', html)
        if result:
            return '{}-{}-{}'.format(result[6:], result[4:6], result[:4])
        result = self.findbyre('(?s)Birth Date</h3><.*?>(?:\(.*?\))?([^<>]*?)</ul>', html) or\
                 self.findbyre('[\s\(]b\.\s+([\w\-/]+)', html) or\
                 self.findbyre('skos:prefLabel">[^<>]*, (\d+)-', html)
        if result and not '[' in result:
            m = re.match('(\d+)[/\-](\d+)[/\-](\d+)', result)
            if m:
                result = '{}-{}-{}'.format(
                    m.group(2),
                    m.group(1),
                    m.group(3) if len(m.group(3)) > 2 else '19' + m.group(3)
                )
            return result
    
    def finddeathdate(self, html):
        result = self.findbyre('<li><h3>Death Date</h3><ul[^<>]*>(\d{8})<', html)
        if result:
            return '{}-{}-{}'.format(result[6:], result[4:6], result[:4])
        result = self.findbyre('(?s)Death Date</h3><.*?>(?:\(.*?\))?([^<>]*?)</ul>', html) or \
                   self.findbyre('skos:prefLabel">[^<>]*, \d+-(\d+)', html)
        if result and not '[' in result:
            m = re.match('(\d+)[/\-](\d+)[/\-](\d+)', result)
            if m:
                result = '{}-{}-{}'.format(
                    m.group(2),
                    m.group(1),
                    m.group(3) if len(m.group(3)) > 2 else '19' + m.group(3)
                )
            return result

    def findbirthplace(self, html):
        return self.findbyre('(?s)Birth Place</h3><.*?>(?:\([^<>]*\))?([^<>]+)\s*(?:\([^<>]*\))?\s*</?[au]', html, 'city')

    def finddeathplace(self, html):
        return self.findbyre('(?s)Death Place</h3><.*?>(?:\([^<>]*\))?([^<>]+)\s*(?:\([^<>]*\))?\s*</?[au]', html, 'city')

    def findgender(self, html):
        return self.findbyre('(?s)Gender</h3><.*?>([^<>]*)(?:<[^<>]*>|\s)*</ul>', html, 'gender')

    def findoccupations(self, html):
        section = self.findbyre('(?s)Occupation</h3>(.*?)<h3', html)
        if section:
            return self.findallbyre('>([^<>]+)</a>', section, 'occupation')

    def findrelorder(self, html):
        section = self.findbyre('(?s)Affiliation</h3>.*?(<ul.*?</ul>)', html)
        if section:
            for result in self.findallbyre('>([^<>]+)</a', section, 'religious order', skips = ['employer', 'university']):
                if result:
                    return result

    def findemployers(self, html):
        section = self.findbyre('(?s)Affiliation</h3>.*?(<ul.*?</ul>)', html)
        if section:
            return self.findallbyre('>([^<>]+)</a', section, 'employer', alt=['university'])
        
    def findlanguagesspoken(self, html):
        if self.isperson:
            sections = self.findallbyre('(?s)Associated Language[^<>]*</h3>.*?(<ul.*?</ul>)', html)
            result = []
            for section in sections:
                result += self.findallbyre('>([^<>]+)</a', section, 'language')
            return result

    def findworkfields(self, html):
        section = self.findbyre('(?s)Field of Activity</h3>.*?(<ul.*?</ul>)', html)
        if section:
            return self.findallbyre('>([^<>]+)</a', section, 'subject')

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html, includesocial=False)


class UlanAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P245"
        self.dbid = "Q2494649"
        self.dbname = "ULAN"
        self.urlbase = "https://www.getty.edu/vow/ULANFullDisplay?find=&role=&nation=&subjectid={id}"
        self.hrtre = '(Record Type:.*?)Sources and Contributors:'
        self.language = 'en'

    def finddescription(self, html):
        return self.findbyre('(?s)<SPAN CLASS=page>.*?</B>\s*\((.*?)\)', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)<B>Note:\s*</B>(.*?)</', html)

    def findnames(self, html):
        section = self.findbyre('<B>Names:</B>.*<TR>(.*?)</TABLE>', html)
        if section:
            return self.findallbyre('<B>(.*?)<', section)

    def findinstanceof(self, html):
        result = self.findbyre('Record Type:.*?>(.*?)<', html, 'instanceof')
        self.isperson = result == "Q5"
        return result

    def findlastname(self, html):
        if self.isperson:
            return self.findbyre('(?s)<SPAN CLASS=page><B>([^<>]*?),', html, 'lastname')

    def findfirstname(self, html):
        if self.isperson:
            return self.findbyre('(?s)<SPAN CLASS=page><B>[^<>]*?,\s*(\w+)', html, 'firstname')

    def findnationality(self, html):
        if self.isperson:
            return self.findbyre('(?s)Nationalities:.*<SPAN CLASS=page>([^<>]*)\(', html, 'country')

    def country(self, html):
        if not self.isperson:
            return self.findbyre('(?s)Nationalities:.*<SPAN CLASS=page>([^<>]*)\(', html, 'country')

    def findoccupations(self, html):
        if self.isperson:
            section = self.findbyre('(?s)>Roles:<.*?<TR>(.*?)</TABLE>', html)
            if section:
                return self.findallbyre('>([^<>\(\)]+)[<\(]', section, 'occupation')

    def findgender(self, html):
        return self.findbyre('Gender:<.*?>(.*?)<', html, 'gender')

    def findbirthplace(self, html):
        return self.findbyre('Born:.*?>([^<>]*)\(', html, 'city')

    def finddeathplace(self, html):
        return self.findbyre('Died:.*?>([^<>]*)\(', html, 'city')

    def findlocation(self, html):
        if not self.isperson:
            return self.findbyre('location:.*?<A.*?>([^<>]*)\(', html, 'city')

    def findbirthdate(self, html):
        if self.isperson:
            result = self.findbyre('</B>\s*\([^<>]*,([^<>]*)-', html)
            if result and not 'ctive' in result:
                return result

    def finddeathdate(self, html):
        if self.isperson:
            part = self.findbyre('</B>\s*\([^<>]*,([^<>]*-[^<>\)]*)', html)
            if part and not 'ctive' in part:
                return self.findbyre('-([^<>\)]*)', part)

    def findworkplaces(self, html):
        return self.findallbyre('>active:(?:\s|&nbsp;|<[^<>]*>)*([^<>]*)\(', html, 'city')

    def findchildren(self, html):
        return self.findallbyre('(?s)>parent of.*?<A[^<>]*>(.*?)<', html, 'person')

    def findfather(self, html):
        return self.findallbyre('(?s)>child of.*?<A[^<>]*>(.*?)<', html, 'male-person')

    def findmother(self, html):
        return self.findallbyre('(?s)>child of.*?<A[^<>]*>(.*?)<', html, 'female-person')

    def findsiblings(self, html):
        return self.findallbyre('(?s)>sibling of.*?<A[^<>]*>(.*?)<', html, 'person')

    def findstudents(self, html):
        return self.findallbyre('(?s)>teacher of.*?<A[^<>]*>(.*?)<', html, 'artist')
 
    def findteachers(self, html):
        return self.findallbyre('(?s)>sibling of.*?<A[^<>]*>(.*?)<', html, 'artist')


class BnfAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P268"
        self.dbid = "Q19938912"
        self.dbname = "Bibliothèque nationale de France"
        self.urlbase = "http://catalogue.bnf.fr/ark:/12148/cb{id}"
        self.hrtre = '(<div class="notice" id="ident">.*?)<div class="notice line"'
        self.language = 'fr'
        self.escapehtml = True

    def finddescriptions(self, html):
        return self.findallbyre('<meta name="DC.subject" lang="fre" content="(.*?)"', html)

    def findnames(self, html):
        return self.findallbyre('<span class="gras">(.*?)<', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)<div[^<>]*"description">(.*?)</div>', html)

    def findinstanceof(self, html):
        self.isperson = "Notice de personne" in html
        if self.isperson:
            return "Q5"
        else:
            return self.findbyre('(?s)Type de[^<>]+:.*?>([^<>]*)</', html, 'instanceof')

    def findnationality(self, html):
        if self.isperson:
            return self.findbyre('(?s)Pays[^<>]*:.*?<span.*?>(.*?)</', html, 'country')

    def findcountry(self, html):
        if not self.isperson:
            return self.findbyre('(?s)Pays[^<>]*:.*?<span.*?>(.*?)</', html, 'country')

    def findlanguagesspoken(self, html):
        if self.isperson:
            result = []
            section = self.findbyre('(?s)Langue\(s\).*?(<.*?>)\s*</div>', html)
            if section:
                section = self.TAGRE.sub(' ', section)
                result = self.findallbyre('([\w&;]{3,})', section, 'language')
            result += self.findallbyre('aussi(?: écrit)? en ([\w]+)', html, 'language')
            result += self.findallbyre('aussi(?: écrit)? en [\w\s]+ et en ([\w]+)', html, 'language')
            return result

    def findgender(self, html):
        return self.findbyre('(?s)Sexe[^<>]+:.*?<span.*?>(.*?)</', html, 'gender')

    def findbirthdate(self, html):
        section = self.findbyre('(?s)Naissance.*?(<.*?>)\s*</div>', html)
        if section:
            result = self.findbyre('>([^<>]+?),', section) or self.findbyre('>([^<>]+?)</', section)
            if result and ".." not in result and re.search("\d{4}", result):
                return result

    def findbirthplace(self, html):
        section = self.findbyre('(?s)Naissance.*?(<.*?>)\s*</div>', html)
        if section:
            return self.findbyre(',([^<>]+)<', section, 'city')

    def finddeathdate(self, html):
        section = self.findbyre('(?s)Mort[^<>]*:.*?(<.*?>)\s*</div>', html)
        if section:
            result = self.findbyre('>([^<>]+?),', section) or self.findbyre('>([^<>]+?)</', section)
            if result and re.search("\d{4}", result):
                return result

    def finddeathplace(self, html):
        section = self.findbyre('(?s)Mort[^<>]*:.*?(<.*?>)\s*</div>', html)
        if section:
            return self.findbyre(',([^<>]+)<', section, 'city')

    def findisni(self, html):
        return self.findbyre('ISNI ([\d\s]*)', html) or self.findbyre('isni/(\w+)', html)

    def findoccupations(self, html):
        section = self.findbyre('(?s)"description">\s*<span[^<>]*>(.*?)</span>', html)
        if section:
            result = []
            for subsection in section.split(' et '):
                result += self.findallbyre('(\w[\-\s\w&\']+)', subsection, 'occupation')
            return result

    def findworkfields(self, html):
        return self.findallbyre("[Pp]rofesseur d[eu']([\w\s]+)? [àa]u?x? ", html, 'subject') +\
               self.findallbyre("[Ss]pécialiste d[eu']s?([\w\s]+) [àa]u?x? ", html, 'subject') +\
               self.findallbyre("[Ss]pécialisée? en ([\w\s]+) [àa]u?x? ", html, 'subject') +\
               self.findallbyre("[Pp]rofesseur d[eu']([\w\s]+)", html, 'subject') +\
               self.findallbyre("[Ss]pécialiste d[eu']s?([\w\s]+)", html, 'subject') +\
               self.findallbyre("[Ss]pécialisée? en ([\w\s]+)", html, 'subject')

    def findemployers(self, html):
        sections = self.findallbyre('En poste\s*:(.*?)[\(<]', html)
        result = []
        for section in sections:
            result += self.findallbyre('([^;]*)', section, 'employer', alt=['university'])
        return result


class SudocAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P269"
        self.dbid = "Q47757534"
        self.dbname = "SUDOC"
        self.urlbase = "https://www.idref.fr/{id}"
        self.hrtre = '(<div id="editzone">.*?)<p>Informations sur la notice</p>'
        self.language = 'fr'
        self.escapehtml = True

    def finddescriptions(self, html):
        return self.findallbyre('(?s)Notice de type</span>.*?([^<>]*)</span>', html) +\
            self.findallbyre('(?s)<span class="detail_label">Note publique d\'information.*?"detail_value">(.*?)<', html)

    def findnames(self, html):
        result = []
        section = self.findbyre("(?s)<p>Point d'accès autorisé</p>(.*)<p>", html)
        if section:
            result += self.findallbyre('(?s)<b>(.*?)[\(<]', section)
        section = self.findbyre("(?s)<p>Variantes de point d'accès</p>(.*)<p>", html)
        if section:
            result += self.findallbyre('(?s)<b>(.*?)[\(<]', section)
        return result

    def findlongtext(self, html):
        return '\n'.join(self.findallbyre('(?s)<span class="detail_value">(.*?)</span>', html))

    def findinstanceof(self, html):
        return self.findbyre('(?s)Notice de type</span>.*?([^<>]*)</span>', html, 'instanceof')

    def findlanguagesspoken(self, html):
        section = self.findbyre('(?s)<span id="Langues" class="DataCoded">(.*?)</span>', html)
        if section:
            return self.findallbyre('(\w+)', section, 'language')

    def findnationality(self, html):
        return self.findbyre('(?s)<span id="PaysISO3166" class="DataCoded">(.*?)</span>', html, 'country')

    def findbirthdate(self, html):
        result = self.findbyre('(?s)Date de naissance[^<>]*</b><span[^<>]*>([^<>]*)<', html)
        if result:
            return "".join([char for char in result if char in "0123456789-"])
    
    def finddeathdate(self, html):
        result = self.findbyre('(?s)Date de mort[^<>]*</b><span[^<>]*>([^<>]*)<', html)
        if result:
            return "".join([char for char in result if char in "0123456789-"])

    def findgender(self, html):
        return self.findbyre('<span id="Z120_sexe" class="DataCoded">(.*?)</span>', html, 'gender')

    def findisni(self, html):
        return self.findbyre('http://isni.org/isni/(\w+)', html)

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html)

    def findbirthplace(self, html):
        return self.findbyre('ieu de naissance.? (.*?)[\.<>]', html, 'city')

    def finddeathplace(self, html):
        return self.findbyre('ieu de décès.? (.*?)[\.<>]', html, 'city')

    def findoccupations(self, html):
        sections = self.findallbyre('(?s)<div class="detail_chaqueNoteBio">.*?<span class="detail_value">(.*?)<', html)
        result = []
        for section in sections:
            for sectionpart in section.split(" et "):
                result += self.findallbyre('([^\.,;]+)', sectionpart, 'occupation')
        return result


class CiniiAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P271"
        self.dbid = "Q10726338"
        self.dbname = "CiNii"
        self.urlbase = "https://ci.nii.ac.jp/author/{id}"
        self.hrtre = '(<div class="itemheading authordata">.*?)<div class="resultlist">'
        self.language = 'ja'

    def findnames(self, html):
        section = self.findbyre('(?s)<h1[^<>]>(.*?)</h1>', html) or ''
        return self.findallbyre('(?s)<span>(.*?)(?:, b\. \d+)?\s*</span>', section) +\
               self.findallbyre('"seefm">(.*?)(?:, b\. \d+)?\s*[<\(（]', html)

    def findinstanceof(self, html):
        return "Q5"

    def findfirstname(self, html):
        return self.findbyre('(?s)<h1[^<>]*>[^<>]*<span>[^<>]*?,\s*(\w+)', html, 'firstname')

    def findlastname(self, html):
        return self.findbyre('(?s)<h1[^<>]*>[^<>]*<span>([^<>]+?),', html, 'lastname')

    def findbirthdate(self, html):
        return self.findbyre(', b\. (\d+)', html)
        

        
class ImdbAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P345"
        self.dbid = "Q37312"
        self.dbname = "Internet Movie Database"
        self.urlbase = None
        if self.isfilm:
            self.hrtre = '(<h1.*?)<h2>Frequently Asked Questions'
        elif self.isperson:
            self.hrtre = '(<h1.*?</table>)'
        self.language = 'en'
        self.escapeurl = True

    @property
    def url(self):
        if self.isfilm:
            return "https://www.imdb.com/title/{id}/".format(id=self.id)
        elif self.isperson:
            return "https://www.imdb.com/name/{id}/".format(id=self.id)
        else:
            return None

    @property
    def isfilm(self):
        return self.id.startswith("tt")

    @property
    def isperson(self):
        return self.id.startswith("nm")

    def finddescription(self, html):
        result = self.findbyre('<meta name="description" content="(.*?)"', html)
        if result:
            return ".".join(result.split(".")[:2])

    def findlongtext(self, html):
        return self.findbyre('(?s)<div class="inline">(.*?)<', html)

    def findnames(self, html):
        return [(self.findbyre('\'og:title\' content="(.*)"', html) or "").replace(" - IMDb", "")]

    def findinstanceof(self, html):
        if self.isfilm:
            return "Q11424"
        elif self.isperson:
            return "Q5"

    def findorigcountry(self, html):
        if self.isfilm:
            return self.findbyre('(?s)Country:.*?>([^<>]+)</a>', html, 'country')

    def findpubdate(self, html):
        if self.isfilm:
            return self.findbyre('span id="titleYear">\(\s*(?:<[^<>]*>)?(.*?)</', html)

    def findmoviedirectors(self, html):
        section = self.findbyre('(?s)>Director:(<.*?</div>)', html)
        if section:
            return self.findallbyre('"name">([^<>]*)</span>', section, 'filmmaker')

    def findscreenwriters(self, html):
        section = self.findbyre('(?s)>Writer:(<.*?</div>)', html)
        if section:
            return self.findallbyre('"name">([^<>]*)</span>', section, 'filmmaker')

    def findcast(self, html):
        section = self.findbyre('(?s)>Credited cast:(<.*?</table>)', html)
        if section:
            return self.findallbyre('"name">([^<>]*)</span>', section, 'actor')

    def findprodcoms(self, html):
        section = self.findbyre('(?s)>Production Co:(<.*?</div>)', html)
        if section:
            return self.findallbyre('"name">([^<>]*)</span>', section, 'filmcompany')

    def findgenres(self, html):
        section = self.findbyre('(?s)>Genres:(<.*?</div>)', html)
        if section:
            return self.findallbyre('(?s)>([^<>]*)</a>', section, 'genre')
       
    def findoriglanguages(self, html):
        section = self.findbyre('(?s)>Language:(<.*?</div>)', html)
        if section:
            return self.findallbyre('(?s)>([^<>]*)</a>', section, 'language')
       
    def finddurations(self, html):
        section = self.findbyre('(?s)>Runtime:(<.*?</div>)', html)
        if section:
            return [self.findbyre('(?s)>([^<>]*)</time>', section)]
    
    def findcolors(self, html):
        result = self.findbyre('(?s)>Color:.*?>([^<>]+)</a>', html)
        if result:
            return [result]

    def findoccupations(self, html):
        section = self.findbyre('(?s)"jobTitle": (".*?"|\[.*?\])', html)
        if section:
            occupations = self.findallbyre('"(.*?)"', section, 'film-occupation', alt=['occupation'])
            return ['Q2526255' if result == 'Q3455803' else result for result in occupations]

    def findbirthdate(self, html):
        return self.findbyre('"birthDate": "(.*?)"', html)

    def finddeathdate(self, html):
        return self.findbyre('"deathDate": "(.*?)"', html)

    def findbirthplace(self, html):
        return self.findbyre('birth_place=(.*?)[&"]', html, 'city')

    def finddeathplace(self, html):
        return self.findbyre('death_place=(.*?)[&"]', html, 'city')


class SbnAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P396"
        self.dbid = None
        self.dbname = "SBN"
        self.urlbase = "http://opac.sbn.it/opacsbn/opac/iccu/scheda_authority.jsp?bid={id}"
        self.hrtre = '(<tbody>.*?</tbody>)'
        self.language = 'it'

    def findnames(self, html):
        result = [self.findbyre('(?s)Nome autore.*?<a .*?>(.*?)[<&\(]', html)]
        section = self.findbyre('(?s)Forme varianti.*?(<.*?)</tr>', html)
        if section:
            result += self.findallbyre('(?s)>([^<>]*)</div>', section)
        return result

    def finddescription(self, html):
        return self.findbyre('(?s)Nota informativa.*?"detail_value">(.*?)<', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)Nota informativa.*?"detail_value">(.*?)<', html)               

    def findinstanceof(self, html):
        return self.findbyre('(?s)Tipo autore.*?detail_value">(.*?)</td>', html, 'instanceof')

    def findbirthdate(self, html):
        return self.findbyre('(?s)Datazione\s*</td>\s*<td[^<>]*>(?:[^<>]*,)?([^<>]*?)-', html)

    def finddeathdate(self, html):
        return self.findbyre('(?s)Datazione\s*</td>\s*<td[^<>]*>[^<>]*-(.*?)<', html)

    def findoccupations(self, html):
        section = self.findbyre('(?s)Nota informativa.*?detail_value">([^<>]*?)\.', html)
        if section:
            if "," in section or ";" in section:
                return self.findallbyre('([^,;]+)', section, 'occupation')
            else:
                return self.findallbyre('(\w{3,})', section, 'occupation')

    def findbirthplace(self, html):
        return self.findbyre('Nato ad? ([^<>]+) e morto', html, 'city') or\
               self.findbyre('Nato ad? ([^<>]+?)[,\(\.]', html, 'city') or\
               self.findbyre('Nato e morto ad? ([^<>,\(\.]+)', html, 'city') or\
               self.findbyre('Nato ad? ([^<>\.]+)', html, 'city')

    def finddeathplace(self, html):
        return self.findbyre('[mM]orto ad? ([^<>\.\(]+) nel', html, 'city') or\
               self.findbyre('[mM]orto ad? ([^<>\.\(]+)', html, 'city')

    def findlanguagesspoken(self, html):
        section = self.findbyre('Lingua.*?detail_value">(.*?)<', html)
        if section:
            return self.findallbyre('(\w{3,})', section, 'language')
                
    def findisni(self, html):
        return self.findbyre('http://isni.org/isni/(\w+)', html)
    
    def findrelorder(self, html):
        section = self.findbyre('(?s)Nota informativa.*?detail_value">([^<>]*?)\.', html) or ""
        if "gesuita" in section.lower():
            return "Q36380"


class LibrariesAustraliaAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P409"
        self.dbid = None
        self.dbname = "National Library of Australia"
        self.urlbase = "https://librariesaustralia.nla.gov.au/search/display?dbid=auth&id={id}"
        self.hrtre = '<!--Record summary-->(.*?)<!--Record summary-->'
        self.language = 'en'

    def finddescription(self, html):
        return self.findbyre('(?s)Heading:.*?">([^<>])*</a>', html)

    def findnames(self, html):
        result = self.findallbyre('(?s)<title>([^<>]*?)(?:<|\(|\s-\s)', html)
        return [','.join(r.split(',')[:2]) for r  in result]

    def findbirthdate(self, html):
        result = self.findbyre('(?s)<dt>Birth:</dt>.*?<li>(.*?)-?</li>', html)
        if result:
            if not 'approx' in result and not 'active' in result:
                return result
        else:
            section = self.findbyre('(?s)<dt>Heading:</dt>.*?>([^<>]*)</a', html)
            if section and not 'approx' in section and not 'active' in section:
                result = self.findbyre(',([^,]*)-', section)
                if result:
                    return result
                else:
                    return section

    def findbirthplace(self, html):
        result = self.findbyre('(?s)<dt>Birth:</dt>(?:\s|<[^<>]*>)*<li>[^<>]*</li>\s*<li>(.*?)</li>', html)
        if result:
            return self.getdata('city', result)
    
    def finddeathdate(self, html):
        result = self.findbyre('(?s)<dt>Death:</dt>.*?<li>(.*?)</li>', html)
        if result:
            if not 'approx' in result:
                return result
        else:
            section = self.findbyre('(?s)<dt>Heading:</dt>.*?>([^<>]*)-?</a', html)
            if section:
                result = self.findbyre('-([^,\-]*)', section)
                if result and not 'approx' in result:
                    return result

    def findfirstname(self, html):
        section = self.findbyre('(?s)<dt>Heading:</dt>.*?>([^<>]*)</a', html)
        pywikibot.output(section)
        if section:
            return self.findbyre(',\s*(\w+)', section, 'firstname')

    def findlastname(self, html):
        section = self.findbyre('(?s)<dt>Heading:</dt>.*?>([^<>]*)</a', html)
        if section:
            return self.findbyre('([^,]*),', section, 'lastname')
        
    def finddeathplace(self, html):
        result = self.findbyre('(?s)<dt>Death:</dt>(?:\s|<[^<>]*>)*<li>[^<>]*</li>\s*<li>(.*?)</li>', html)
        if result:
            return self.getdata('city', result)

    def findoccupations(self, html):
        section = self.findbyre('(?s)<dt>Occupations:</dt>.*?<li>(.*?)</li>', html)
        if section:
            return self.findallbyre('(\w+)', section, 'occupation')

    def findmixedrefs(self, html):
        result = self.findbyre('(?s)<dt>LC number:</dt>.*?<li>(.*?)</li>', html)
        if result:
            result = result.replace(" ", "")
            results = self.findallbyre('[a-z]+\d+', result)
            return [("P244", result) for result in results]


class MusicBrainzAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P434"
        self.dbid = "Q19832969"
        self.dbname = "MusicBrainz"
        self.urlbase = "https://musicbrainz.org/artist/{id}"
        self.urlbase3 = "https://musicbrainz.org/artist/{id}/relationships"
        self.hrtre = '(<h2 class="artist-information">.*?)<div id="footer">'
        self.language = 'en'

    def finddescription(self, html):
        return self.findbyre('<div class="wikipedia-extract-body wikipedia-extract-collapse"><p>(.+?)</p>', html)

    def findnames(self, html):
        return self.findallbyre('(?s)<dd class="sort-name">(.*?)</dd>', html)

    def findinstanceof(self, html):
        result = self.findbyre('<dd class="type">(.*?)</dd>', html, 'instanceof')
        self.isperson = result == "Q5"
        return result

    def findinception(self, html):
        return self.findbyre('(?s)<dt>Founded:</dt>.*?<dd>(.*?)</dd>', html)

    def finddissolution(self, html):
        return self.findbyre('(?s)<dt>Dissolved:</dt>.*?<dd>(.*?)[<\(]', html)

    def findformationlocation(self, html):
        return self.findbyre('(?s)<dt>Founded in:</dt>.*?<bdi>(\w+)', html, 'city') or\
               self.findbyre('(?s)<dt>Founded in:</dt>.*?<bdi>(.*?)</bdi>', html, 'city')

    def findorigcountry(self, html):
        if not self.isperson:
            return self.findbyre('(?s)<dt>Area:</dt>.*?<bdi>(.*?)</bdi>', html, 'country')

    def findnationality(self, html):
        if self.isperson:
            return self.findbyre('(?s)<dt>Area:</dt>.*?<bdi>(.*?)</bdi>', html, 'country')

    def findisni(self, html):
        return self.findbyre('/isni/(\w+)', html)

    def findviaf(self, html):
        return self.findbyre('"https://viaf.org/viaf/(\w+)/?"', html)

    def findwebsite(self, html):
        return self.findbyre('(?s)<th>offici.le website:.*?<bdi>(.*?)<', html) or\
               self.findbyre('<li class="home-favicon"><a href="(.*?)">', html)

    def findtwitter(self, html):
        return self.findbyre('<li class="twitter-favicon"><a href="[^"]*">@([^<>]*)</a>', html)

    def findfacebook(self, html):
        return self.findbyre('<li class="facebook-favicon"><a href="https://www.facebook.com/([^/"]+)/?">', html)

    def findgender(self, html):
        return self.findbyre('class="gender">(.*?)</', html, 'gender')

    def findbirthdate(self, html):
        return self.findbyre('(?s)<dt>Born:</dt>.*?<dd[^<>]*>(.*?)[<\(]', html)
    
    def finddeathdate(self, html):
        return self.findbyre('(?s)<dt>Died:</dt>.*?<dd[^<>]*>(.*?)[<\(]', html)

    def findbirthplace(self, html):
        section = self.findbyre('(?s)<dt>Born in:</dt>\s*(<dd.*?</dd>)', html)
        if section:
            return self.getdata('city', self.TAGRE.sub('', section))

    def finddeathplace(self, html):
        section = self.findbyre('(?s)<dt>Died in:</dt>\s*(<dd.*?</dd>)', html)
        if section:
            return self.getdata('city', self.TAGRE.sub('', section))

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html, includesocial=False) +\
               [("P4862", self.findbyre('<li class="amazon-favicon"><a href="[^"]*amazon[^"\?]*/(B\w+)[\?"]', html))]+\
               [("P3453", result) for result in self.findallbyre('<dd class="ipi-code">(.*?)</dd>', html)]

class StructuraeAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P454"
        self.dbid = "Q1061861"
        self.dbname = "Structurae"
        self.urlbase = "http://en.structurae.de/structures/data/index.cfm?ID={id}"
        self.hrtre = '(<h1.*?)Participants</h2>'
        self.language = 'en'

    def finddescription(self,html):
        return self.findbyre('<meta name="Description" content="(.*?)"', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)<div class="js-acordion-body" id="notes">\s*<p>(.*?)</div>', html)

    def findlanguagenames(self, html):
        return [(m[0], m[1].replace("-", " ")) for m in re.findall('(?s)"alternate"[^<>]*hreflang="(\w+)"[^<>]*/([^<>"]*)">', html)]

    def findnames(self, html):
        return [self.findbyre('(?s)<h1[^<>]*>(.*?)<', html),
                self.findbyre('(?s)Name in [^<>]*</th>[^<>]*<td>(.*?)<', html),
                ]

    def findinstanceof(self, html):
        return "Q41176"

    def findinception(self, html):
        return self.findbyre('(?s)<th>Completion.*?>([^<>]+)</a>', html)

    def finduse(self, html):
        return self.findbyre('(?s)Function / usage:.*?>([^<>]+)</a>', html, 'function')

    def findlocation(self, html):
        return self.findbyre("(?s)itemprop='containedInPlace'.*?<strong>(.*?)</", html, 'city')

    def findcountry(self, html):
        return self.findbyre("itemprop='containedInPlace'.*>([^<>]+)</span>", html, 'country')

    def findaddress(self, html):
        return self.findbyre('itemprop="address">([^<>]+)</', html)

    def findcoords(self, html):
        lat = self.findbyre('itemprop="latitude" content="(.*?)"', html)
        lon = self.findbyre('itemprop="longitude" content="(.*?)"', html)
        if (lat and lon):
            return "{} {}".format(lat, lon)

    def findheights(self, html):
        return [self.findbyre('(?s)<td>height</td>.*<td>(.*?)</td>', html)]

    def findfloorsabove(self, html):
        return self.findbyre('(?s)<td>number of floors \(above ground\)</td>.*<td>(.*?)</td>', html)


class SelibrAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P906"
        self.dbid = "Q1798125"
        self.dbname = "LIBRIS"
        self.urlbase = "https://libris.kb.se/auth/{id}"
        #self.urlbase = None
        self.hrtre = '(.*)'
        self.language = 'en'

    def finddescription(self, html):
        return self.findbyre('<h1>(.*?)</', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)<div class="bio">(.*?)</div>', html)
        
    def findinstanceof(self, html):
        return "Q5"

    def findviaf(self, html):
        return self.findbyre('http://viaf.org/viaf/(\w+)', html)

    def findnames(self, html):
        return self.findallbyre('(?s)<h1[^<>]*>[^<>]*:([^<>]*?)[,<]', html)


class BneAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P950"
        self.dbid = None
        self.dbname = "Biblioteca Nacional de España"
        self.urlbase = "http://datos.bne.es/persona/{id}.html"
        self.hrtre = '(<h1.*?)<h3>Descarga en otros formatos'
        self.language = 'es'

    def findnames(self, html):
        return [self.findbyre('"og:title" content="(.*?)[\("]', html)]

    def finddescriptions(self, html):
        return [
            self.findbyre('"og:description" content="([^"]+),', html),
            self.findbyre('"og:description" content="Descubre ([^"]+),', html),
            self.findbyre('"og:description" content="([^"]+)"', html),
            self.findbyre('"og:title" content="(.+?)"', html),
            self.findbyre('(?s)class="bio">.*?<p>(.*?)</p>', html),
            ]

    def findlongtext(self, html):
        return self.findbyre('(?s)<table class="table table-condensed table-responsive">(.*?)</table>', html)

    def findlastname(self, html):
        return self.findbyre('<h1>([^<>]+),', html, 'lastname')

    def findfirstname(self, html):
        return self.findbyre('<h1>[^<>]+,\s*(\w+)', html, 'firstname')

    def findbirthdate(self, html):
        result = self.findbyre('(?s)Año de nacimiento:\s*<span>(.*?)<', html) or\
                 self.findbyre('<h1>[^<>]+\((?:n\.\s*)?([^\)<>-]+?)[–\-\)]', html)
        if result and not "fl." in result and not result.strip().startswith("m.") and "1" in result:
            return result

    def finddeathdate(self, html):
        result = self.findbyre('(?s)Año de fallecimiento:\s*<span>(.*?)<', html)
        if result:
            return result
        preresult = self.findbyre('<h1>(.*?)</h1>', html)
        if preresult and not "fl." in preresult:
            return self.findbyre('<h1>[^<>]+\([^<>]+[–\-]([^<>]+\d{4}[^<>]+)\)', html)

    def findbirthplace(self, html):
        return self.findbyre('(?s)Lugar de nacimiento:\s*<span>(.*?)<', html, 'city')

    def finddeathplace(self, html):
        return self.findbyre('(?s)Lugar de fallecimiento:\s*<span>(.*?)<', html, 'city')

    def findviaf(self, html):
        return self.findbyre('"http://viaf.org/viaf/(\w+)/?"', html)

    def findisni(self, html):
        return self.findbyre('"http://isni-url.oclc.nl/isni/(\w+)"', html)

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html)

    def findoccupations(self, html):
        section = self.findbyre('(?s)<h4>Categoría profesional:(.*?)</h4>', html)
        if section:
            return self.findallbyre('([^<>,]*)', section, 'occupation')

    def findworkfields(self, html):
        section = self.findbyre('(?s)<h4>Campo de actividad:(.*?)</h4>', html)
        if section:
            return self.findallbyre('([^<>,]*)', section, 'subject')

    def findlanguagesspoken(self, html):
        section = self.findbyre('(?s)<h4>>Lengua:(.*?)</h4>', html)
        if section:
            return self.findallbyre('([^<>,])*', section, 'subject')



class OrcidAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P496"
        self.dbid = None
        self.dbname = "Orcid"
        self.urlbase = 'https://orcid.org/{id}'
        self.language = 'en'
        self.hrtre = '(<div class="workspace-section">.*?)</i>\s*Works\('

    def findinstanceof(self, html):
        return "Q5"

    def findnames(self, html):
        return self.findallbyre('(?s)"(?:full|other)-name">(.*?)<', html)

    def finddescriptions(self, html):
        return [
            self.findbyre('(?s)<div class="bio-content">(.*?)<', html),
            self.findbyre('(?s)<div class="bio-content">(.*?)</div>', html)
            ]

    def findlongtext(self, html):
        return self.findbyre('(?s)<div class="bio-content">(.*?)</div>', html)

    def findnationalities(self, html):
        return self.findallbyre('"country">(.*?)<', html, 'country')

    def findschools(self, html):
        pywikibot.output("Check education and affiliations by hand!")


class CbdbAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P497'
        self.dbid = 'Q13407958'
        self.dbname = 'China Biographical Database'
        self.urlbase = 'https://cbdb.fas.harvard.edu/cbdbapi/person.php?id={id}'
        self.language = 'zh'
        self.hrtre = '(<table style="font-size:smaller">.*?)<hr>'

    def findlanguagenames(self, html):
        return [
            ('en', self.findbyre('<b>索引/中文/英文名稱</b>:[^<>]*/([^<>]*)<', html)),
            ('zh', self.findbyre('<b>索引/中文/英文名稱</b>:[^<>]*?/([^<>]*)/', html))
            ]

    def findbirthdate(self, html):
        return self.findbyre('(?s)<b>生年</b>[^<>]*\(([^<>]*?)\)', html)

    def finddeathdate(self, html):
        return self.findbyre('(?s)<b>卒年</b>[^<>]*\(([^<>]*?)\)', html)
        
    def findlongtext(self, html):
        return self.findbyre('(?s)註.*?<td>(.*?)</td>', html)

    def findnationalities(self, html):
        return [
            self.findbyre('(?s)<b>生年</b>:\s*(.)', html, 'dynasty') or\
            self.findbyre('(?s)<b>生年</b>:\s*(..)', html, 'dynasty'),
            self.findbyre('(?s)<b>卒年</b>:\s*(.)', html, 'dynasty') or\
            self.findbyre('(?s)<b>卒年</b>:\s*(..)', html, 'dynasty')
            ]

class FindGraveAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P535"
        self.dbid = "Q63056"
        self.dbname = "Find a Grave"
        self.urlbase = "https://www.findagrave.com/memorial/{id}"
        self.language = 'en'
        self.hrtre = '(<h1.*?</table>)'

    def getvalue(self, name, html, category=None):
        return self.findbyre('%s: "(.*?)"'%name, html, category)

    def findnames(self, html):
        f = open('result.html',  'w')
        f.write(html)
        f.close()
        return [self.getvalue('shareTitle', html)]

    def findlongtext(self, html):
        return self.findbyre('(?s) id="fullBio">(.*?)<', html)

    def finddeathdate(self, html):
        return self.getvalue('deathDate', html) or\
               self.findbyre('"deathDate">(.*?)<', html) or\
               self.getvalue('deathYear', html)

    def findburialplace(self, html):
        return self.getvalue('cemeteryName', html, 'cemetary') or\
               self.getvalue('cemeteryCityName', html, 'city') or\
               self.getvalue('locationName', html, 'city')

    def findfirstname(self, html):
        return self.getvalue('firstName', html, 'firstname')

    def findlastname(self, html):
        return self.getvalue('lastName', html, 'lastname')

    def findbirthdate(self, html):
        return self.findbyre('"birthDate">(.*?)<', html) or\
               self.getvalue('birthYear', html)

    def findbirthplace(self, html):
        return self.findbyre('"birthPlace">(.*?)<', html, 'city')
                 
    def finddeathplace(self, html):
        return self.findbyre('"deathPlace">(.*?)<', html, 'city')

    def findfather(self, html):
        result = self.getvalue('fatherName', html, 'person')
        if result:
            return result
        section = self.findbyre('(?s)>Ouders</b>(.*?)</ul>', html)
        if section:
            result = self.findallbyre('(?s)<h4[^<>]*>(.*?)</h4>', section, 'male-person')
            result = [r for r in result if r]
            if result:
                return result[0]

    def findmother(self, html):
        result = self.getvalue('motherName', html, 'person')
        if result:
            return result
        section = self.findbyre('(?s)>Ouders</b>(.*?)</ul>', html)
        if section:
            result = self.findallbyre('(?s)<h4[^<>]*>(.*?)</h4>', section, 'female-person')
            result = [r for r in result if r]
            if result:
                return result[0]

    def findspouses(self, html):
        result = self.findallbyre('sp\d+Name: "(.*?)"', html, 'person')
        if result:
            return result
        section = self.findbyre('(?s)>Partners</b>(.*?)</ul>', html)
        if section:
            return self.findallbyre('(?s)<h4[^<>]*>(.*?)</h4>', section, 'person')

    def findsiblings(self, html):
        section = self.findbyre('(?s)>Broer[^<>]*zus[^<>]*</b>(.*?)</ul>', html)
        if section:
            return self.findallbyre('(?s)<h4[^<>]*>(.*?)</h4>', section, 'person')

    def findchildren(self, html):
        section = self.findbyre('(?s)>Kinderen</b>(.*?)</ul>', html)
        if section:
            return self.findallbyre('(?s)<h4[^<>]*>(.*?)</h4>', section, 'person')


class IpniAuthorsAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P586'
        self.dbid = 'Q922063'
        self.dbname = 'International Plant Names Index'
        self.urlbase = 'http://www.ipni.org/ipni/idAuthorSearch.do?id={id}'
        self.language = 'en'
        self.hrtre= '</h2>(.*?)<p>View the'

    def findinstanceof(self, html):
        return 'Q5'
        
    def findnames(self, html):
        result = self.findallbyre('(?s)<h3>(.*?)[\(<]', html)
        section = self.findbyre('(?s)<h4>Alternative Names:\s*</h4(>.*?<)h/d', html)
        if section:
            result += self.findallbyre('(?)>([^<>]*)<', section)
        return result

    def findlastname(self, html):
        return self.findbyre('(?s)<h3>([^<>]*?),', html, 'lastname')

    def findfirstname(self, html):
        return self.findbyre('(?s)<h3>[^<>]*,\s*(\w+)', html, 'firstname')

    def findlongtext(self, html):
        return self.findbyre('(?s)<h4>Comment:\s*</h4>(.*?)<h\d', html)

    def findbirthdate(self, html):
        return self.findbyre('(?s)<h3>[^<>]*\((\d+)-', html)

    def finddeathdate(self, html):
        return self.findbyre('(?s)<h3>[^<>]*\([^<>]*?-(\d+)\)', html)

    def findmixedrefs(self, html):
        return [('P428', self.findbyre('(?s)<h4>Standard Form:\s*</h4>\s*<p>(.*?)<', html))]

    def findworkfields(self, html):
        section = self.findbyre('(?s)<h4>Area of Interest:\s*</h4>\s*<p>(.*?)</p>', html)
        if section:
            return self.findallbyre('([^,]*)', section, 'subject')

    def findsources(self, html):
        section = self.findbyre('(?s)<h4>Information Source:</h4>\s*<p>(.*?)</p>', html)
        if section:
            return self.findallbyre('([^,]*)', section, 'source')

    def findnationalities(self, html):
        section = self.findbyre('(?s)<h4>Countries:\s*</h4>(.*?)(?:<h|<p>View)', html)
        if section:
            return self.findallbyre('(?s)>(.*?)<', section, 'country')

    
class GnisAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P590"
        self.dbid = None
        self.dbname = "GNIS"
        self.urlbase = "https://geonames.usgs.gov/apex/f?p=gnispq:3:::NO::P3_FID:{id}"
        self.language = 'en'

    def findnames(self, html):
        return self.findbyre('Name:</td><td[^<>]*>(.*?)<', html)

    def findinstanceof(self, html):
        return self.findbyre('Class:</td><td[^<>]*>(.*?)[<\(]', html, 'instanceof')

    def findelevations(self, html):
        return [
            self.findbyre('Elevation:</td><td[^<>]*>(\d+)/', html) + ' feet',
            self.findbyre('Elevation:</td><td[^<>]*>\d+/(\d+)', html) + ' m'
            ]

    def findadminloc(self, html):
        return self.findbyre('"COUNTY_NAME">(.*?)<', html, 'county') or\
               self.findbyre('"STATE_NAME">(.*?)<', html, 'county')

    def findcountry(self, html):
        return "Q30"

    def findcoords(self, html):
        lat = self.findbyre('"LAT">(.*?)<')
        lon = self.findbyre('"LONGI">(.*?)<')
        if lat and lon:
            return "{} {}".format(lat, lon)


class MathGenAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P549'
        self.dbid = 'Q829984'
        self.dbname = 'Mathematics Genealogy Project'
        self.urlbase = 'https://www.genealogy.math.ndsu.nodak.edu/id.php?id={id}'
        self.hrtre = '(<h2.*?)We welcome any additional information.'
        self.language = 'en'
        self.escapehtml = True

    def findnames(self, html):
        return [self.findbyre('(?s)<h2[^<>]*>(.*?)<', html)]

    def findinstanceof(self, html):
        return 'Q5'

    def finddegrees(self, html):
        return self.findallbyre('(?s)>\s*(Ph\.D\.)\s*<', html, 'degree')
        
    def findschools(self, html):
        return self.findallbyre('(?s)>\s*Ph\.D\.\s*<[^<>]*>(.*?)<', html, 'university')

    def findadvisors(self, html):
        return self.findallbyre('(?s)Advisor[^<>]*:[^<>]*<[^<>]*>(.*?)<', html, 'scientist')

    def finddocstudents(self, html):
        section = self.findbyre('(?s)Students:.*?<table[^<>]*>(.*?)</table>', html)
        if not section:
            section = self.findbyre('(?s)<th>Descendants</th>(.*?)</table>', html)
        if section:
            return self.findallbyre('(?s)<a[^<>]*>(.*?)<', section, 'scientist')
    

    
class OpenLibraryAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P648"
        self.dbid = "Q1201876"
        self.dbname = "Open Library"
        self.urlbase = "https://openlibrary.org/works/{id}"
        self.hrtre = '(<h1.*?)<h2[^<>]*>[^<>]*(?:edition|work)'
        self.language = 'en'

    @property
    def isperson(self):
        return self.id.endswith("A")

    def finddescription(self, html):
        return self.findbyre('<meta name="description" content="(?:Books by)?(.*?)"', html)

    def findnames(self, html):
        return [self.findbyre('<title>([^<>]*)\|', html)]

    def findlongtext(self, html):
        return self.findbyre('<div id="contentBody">(.*?)<div class="clearfix">', html)

    def findinstanceof(self, html):
        if self.isperson:
            return "Q5"
        else:
            return "Q571"

    def findbirthdate(self, html):
        result = self.findbyre('(?s)<h2 class="author collapse">([^<>-]*\d{4}[^<>-]*)', html)
        if result and not 'fl.' in result:
            return result

    def finddeathdate(self, html):
        section = self.findbyre('(?s)<h2 class="author collapse">([^<>-]*-[^<>-]*\d{4}[^<>,]*)', html)
        if section and not 'fl.' in section:
            return section.split('-')[1]


class RkdArtistsAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P650"
        self.dbid = "Q17299517"
        self.dbname = "RKDartists"
        self.urlbase = "https://rkd.nl/nl/explore/artists/{id}"
        self.hrtre = '(<div class="fieldGroup.*?)<script>'
        self.language = 'nl'
        self.escapehtml = True

    def findinstanceof(self, html):
        return "Q5"

    def finddescription(self, html):
        return self.findbyre('"og:description" content="(.*?)"', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)<div class="left">(.*?)<dt>Permalink</dt>', html)

    def findnames(self, html):
        return [self.findbyre('(?s)itemprop="name">(.*?)<', html)] +\
               [self.findbyre('(?s)<h2[^<>]*>(.*?)<', html)] +\
               self.findallbyre('itemprop="alternateName">(.*?)<', html)

    def findgender(self, html):
        return self.findbyre('(?s)itemprop="gender">(.*?)<', html, 'gender')
    
    def findoccupations(self, html):
        section = self.findbyre('(?s)Kwalificaties\s*</dt>.*?<dd>(.*?)</dd>', html)
        if section:
            return self.findallbyre('">([^<>]+)</span>', section, 'occupation')

    def findbirthplace(self, html):
        return self.findbyre('itemprop="birthPlace">([^<>]*),', html, 'city') or\
               self.findbyre('itemprop="birthPlace">([^<>]*)<', html, 'city')

    def findbirthdate(self, html):
        return self.findbyre('itemprop="birthDate">([^<>]*?)[</]', html)
        
    def finddeathplace(self, html):
        return self.findbyre('itemprop="deathPlace">([^<>]*),', html, 'city') or\
               self.findbyre('itemprop="deathPlace">([^<>]*)<', html, 'city')

    def finddeathdate(self, html):
        return self.findbyre('itemprop="deathDate">([^<>]*?)[</]', html)

    def findworkplaces(self, html):
        section = self.findbyre('(?s)Werkzaam in.*?<ul>(.*?)</ul>', html)
        if section:
            return self.findallbyre('>([^<>]+)</a>', section, 'city')

    def findstudents(self, html):
        section = self.findbyre('(?s)Leraar van.*?<dd>(.*?)</dd>', html)
        if section:
            return self.findallbyre('>([^<>]*)</span>', section, 'artist')
        
    def findteachers(self, html):
        section = self.findbyre('(?s)Leerling van.*?<dd>(.*?)</dd>', html)
        if section:
            return self.findallbyre('>([^<>]*)</span>', section, 'artist')
        
    def findinfluences(self, html):
        section = self.findbyre('(?s)Be.nvloed door.*?<dd>(.*?)</dd>', html)
        if section:
            return self.findallbyre('>([^<>]*)</span>', section, 'artist')
        
    def findschools(self, html):
        section = self.findbyre('(?s)<dt>\s*Opleiding\s*</dt>.*?<dd>(.*?)</dd>', html)
        if section:
            return self.findallbyre('>([^<>]+)</a>', section, 'university')

    def findnationalities(self, html):
        return self.findallbyre('itemprop="nationality">(.*?)<', html, 'country')

    def findgenres(self, html):
        return self.findallbyre('Onderwerpen\s*<em>(.*?)<', html, 'genre')

    def findmovements(self, html):
        return self.findallbyre('Stroming\s*<em>(.*?)<', html, 'movement')
    
    def findsiblings(self, html):
        return self.findallbyre('[bB]roer van ([^<>]*)', html, 'person') +\
            self.findallbyre('[zZ]us(?:ter)? van ([^<>]*)', html, 'person')

    def findfather(self, html):
        return self.findbyre('[zZ]oon van ([^<>]*)', html, 'male-person', skips=['female-person']) or\
               self.findbyre('[dD]ochter van ([^<>]*)', html, 'male-person', skips=['female-person'])

    def findmother(self, html):
        return self.findbyre('[zZ]oon van ([^<>]*)', html, 'female-person', skips=['male-person']) or\
               self.findbyre('[dD]ochter van ([^<>]*)', html, 'female-person', skips=['male-person'])

    def findmemberships(self, html):
        return self.findallbyre('Lid van[^<>]*<em>(.*?)<', html, 'organization')

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html, includesocial=False)
    

class BiografischPortaalAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P651"
        self.dbid = "Q1868372"
        self.dbname = "Biografisch Portaal"
        self.urlbase = "http://www.biografischportaal.nl/persoon/{id}"
        self.hrtre = '(<h1.*)<h2'
        self.language = 'nl'

    def finddescription(self, html):
        return self.findbyre('(?s)<th>(geboren.*?)</table>', html)

    def findnames(self, html):
        return [self.findbyre('(?s)<title>(.*?)<', html)]

    def findlongtext(self, html):
        return self.findbyre('(?s)<div class="levensbeschrijvingen">(.*?)<!-- content end', html)

    def findbirthplace(self, html):
        return self.findbyre('(?s)<th>geboren</th>[^<>]*<td>[^<>]*<span><br\s*/>([^<>]*)<', html, 'city')

    def findbirthdate(self, html):
        result = self.findbyre('(?s)<th>geboren</th>[^<>]*<td>(.*?)<', html)
        if result and "tussen" not in result:
            return result
    
    def finddeathplace(self, html):
        return self.findbyre('(?s)<th>gestorven</th>[^<>]*<td>[^<>]*<span><br\s*/>([^<>]*)<', html, 'city')

    def finddeathdate(self, html):
        result = self.findbyre('(?s)<th>gestorven</th>[^<>]*<td>(.*?)<', html)
        if result and "tussen" not in result:
            return result

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html)

    def findgender(self, html):
        return self.findbyre('(?s)<th>sekse</th>.*?<li>(.*?)<', html, 'gender')

    def findsources(self, html):
        return self.findallbyre('(?s)<a class="external_link open_in_new_window"[^<>]*>(.*?)<', html, 'source')


class NkcrAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P691'
        self.dbid = 'Q13550863'
        self.dbname = 'NKC'
        self.urlbase = 'https://aleph.nkp.cz/F/?func=find-c&local_base=aut&ccl_term=ica={id}'
        self.language = 'cs'
        self.hrtre = '(<table width=100%>.*?)<script language='

    def prepare(self, html):
        return html.replace('&nbsp;', ' ')

    def getvalue(self, field, html, dtype=None):
        return self.findbyre('(?s)<td[^<>]*>\s*{}\s*</td>\s*<td[^<>]*>(?:<[^<>]*>)*(.*?)<'.format(field), html, dtype)

    def findlongtext(self, html):
        return self.getvalue('Biogr\./Hist\. .daje', html)

    def findinstanceof(self, html):
        return 'Q5'

    def findnames(self, html):
        result = [
            self.getvalue('Z.hlav.', html),
            self.getvalue('Pseudonym', html)
            ]
        return [','.join(r.split(',')[:-1]) for r in result if r]

    def finddescription(self, html):
        return self.getvalue('Biogr\./Hist\. .daje', html)
        
    def findnationality(self, html):
        result = self.getvalue('Související zem.', html, 'country')
        if result:
            return result
        section = self.getvalue('Biogr\./Hist\. .daje', html)
        if section:
            return self.findbyre('(\w+)', section, 'country')
    
    def findbirthdate(self, html):
        return self.findbyre('[Nn]arozen ([\d\.\s]*)', html)

    def finddeathdate(self, html):
        return self.findbyre('[Zz]em.ela? ([\d\.\s]*)', html)

    def findbirthplace(self, html):
        return self.findbyre('[Nn]arozen [\d\.\s]* v ([\w\s]*)', html, 'city')

    def finddeathplace(self, html):
        return self.findbyre('[Zz]em.ela [\d\.\s]* v ([\w\s]*)', html, 'city')

    def findoccupations(self, html):
        section = self.getvalue('Biogr\./Hist\. .daje', html)
        if section:
            if 'special' in section:
                section = section[:section.find('special')]
            parts = section.split(' a ')
            result = []
            for part in parts:
                result += self.findallbyre('([^\,\.;]*)', part, 'occupation')
            return result

    def findrelorder(self, html):
        return self.getvalue('Související org\.', html, 'religious order')

    def findlanguagesspoken(self, html):
        section = self.getvalue('Jazyk', html)
        if section:
            return self.findallbyre('([^;]+)', section, 'language')

    def findworkfields(self, html):
        results = []
        for regex in [
            '[oO]dborník v (.*?)[\.<]',
            '[sS]pecial\w* (?:se )?(?:v|na) (.*?)[\.<]',
            '[zZ]abývá se (.*?)[\.<]',
            'Zaměřuje se na (.*?)[\.<]',
            '[oO]boru (.*?)[\.<]',
        ]:
            sections = self.findallbyre(regex, html)
            for section in sections:
                parts = section.split(' a ')
                for part in parts:
                    if part.startswith('v '):
                        part = part[2:]
                    results += self.findallbyre('([\w\s]+)', part.replace(' v ', ' '), 'subject')
        return results


class DbnlAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P723'
        self.dbid = 'Q2451336'
        self.dbname = 'DBNL'
        self.urlbase = 'http://www.dbnl.org/auteurs/auteur.php?id={id}'
        self.language = 'nl'
        self.hrtre = '(<p><span class="label">.*?)<form class="mainsearchform"'
        self.escapehtml = True

    def findnames(self, html):
        return [
            self.findbyre('<title>(.*?)[&<·]', html),
            self.findbyre('"naam">(?:<[^<>]*>)*([^<>]+)<', html),
            self.findbyre('href="#naam">(.*?)<', html),
            ]

    def findlongtext(self, html):
        return self.findbyre('(?s)<article[^<>]*>(.*?)</article>', html)

    def findbirthdate(self, html):
        return self.findbyre('>geboren(?:<[^<>]*>)*<i>(.*?)<', html)

    def findbirthplace(self, html):
        return self.findbyre('>geboren.*? te (?:<[^<>]*>)*([^<>]+)<', html, 'city')

    def finddeathdate(self, html):
        return self.findbyre('>overleden(?:<[^<>]*>)*<i>(.*?)<', html)

    def finddeathplace(self, html):
        return self.findbyre('>overleden<.*?> te (?:<[^<>]*>)*([^<>]+)<', html, 'city')

    def findwebpages(self, html):
        section = self.findbyre('(?s)<section id="websites">.*?<table>(.*?)</table>', html)
        if section:
            return self.findallbyre('>([^<>]*)</a>', section)

    def findsources(self, html):
        section = self.findbyre('(?s)<h2>Biografie[^<>]*</h2>(.*?)</table>', html)
        if section:
            return self.findallbyre('>([^<>]*)</a>', section, 'source')

    def findwebpages(self, html):
        section = self.findbyre('(?s)<h2>Biografie[^<>]*</h2>(.*?)</table>', html)
        if section:
            results = self.findallbyre('<a href="(.*?)"', section)
            return ['https://www.dbnl.org/' + result.lstrip('/') for result in results]


class SikartAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P781'
        self.dbid = 'Q683543'
        self.dbname = 'SIKART'
        self.urlbase = 'http://www.sikart.ch/KuenstlerInnen.aspx?id={id}'
        self.language = 'de'
        self.hrtre = '<!-- content_start -->(.*?)<!-- content_end -->'
        self.escapehtml = True

    def getvalue(self, field, html, dtype=None):
        return self.findbyre('(?s)>%s<.*?<div[^<>]*>(.*?)<'%field, html, dtype)

    def findinstanceof(self, html):
        return 'Q5'

    def findnames(self, html):
        return [
            self.findbyre('<title>([^<>]+?)-', html),
            self.findbyre('<h1>(.*?)<', html)
            ]

    def finddescriptions(self, html):
        return [
            self.getvalue('Vitazeile', html),
            self.getvalue('Vitazeile', html).split('.')[0]
            ]

    def findlongtext(self, html):
        return self.findbyre('(?s)<!-- content_start -->(.*)<!-- content_end -->', html)

    def findlastname(self, html):
        return self.findbyre('token.lastname=(\w+)', html, 'lastname')

    def findfirstname(self, html):
        return self.findbyre('token.firstname=(\w+)', html, 'firstname')

    def findbirthdate(self, html):
        dates = self.getvalue('Lebensdaten', html)
        if dates:
            return self.findbyre('\*\s*([\d\.]+)', dates)

    def findbirthplace(self, html):
        dates = self.getvalue('Lebensdaten', html)
        if dates:
            return self.findbyre('\*\s*[\d\.]+\s*(.*?),', dates, 'city')

    def finddeathdate(self, html):
        dates = self.getvalue('Lebensdaten', html)
        if dates:
            return self.findbyre('†(?:\s|&nbsp;)*([\d\.]+)', dates)

    def finddeathplace(self, html):
        dates = self.getvalue('Lebensdaten', html)
        if dates:
            return self.findbyre('†(?:\s|&nbsp;)*[\d\.]+(.*)', dates, 'city')
        
    def findchoriginplaces(self, html):
        section = self.getvalue('Bürgerort', html)
        if section:
            return self.findallbyre('([\w\s\-]+)', section, 'city')

    def findnationality(self, html):
        return self.getvalue('Staatszugehörigkeit', html, 'country')

    def findoccupations(self, html):
        section = self.getvalue('Vitazeile', html)
        if section:
            result = []
            if ' et ' in section:
                splitter = 'et'
            else:
                splitter = 'und'
            for subsection in section.split('.')[0].split(' %s '%splitter):
                result += self.findallbyre('([\w\s]+)', subsection, 'occupation')
            return result

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html)

    def findwebpages(self, html):
        section = self.findbyre('Datenbanken</div>(.*?)</tr>', html)
        if section:
            return self.findallbyre('<a href="(.*?)"', section)


class ImslpAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P839'
        self.dbid = 'Q523660'
        self.dbname = 'International Music Score Library Project'
        self.urlbase = 'https://imslp.org/wiki/{id}'
        self.isperson = self.id.startswith('Category:')
        self.hrtre = '(<h\d.*?)<h2'
        self.language = 'nl'

    def findinstanceof(self, html):
        if self.isperson:
            return 'Q5'
        else:
            raise NotImplementedError # analysis only made for persons
            return 'Q207628'

    def findbirthdate(self, html):
        return self.findbyre('</h2>\(([^<>]*?)—', html)

    def finddeathdate(self, html):
        return self.findbyre('</h2>\([^<>]*?—([^<>]*?)\)', html)

    def findlanguagenames(self, html):
        result = [('nl', x) for x in self.findallbyre('<h2>\s*<span[^<>]*>(.*?)</span>', html)]
        section = self.findbyre('Andere Namen/Transliteraties:(.*?)<', html)
        if section:
            parts = section.split(',')
            for part in parts:
                subparts = self.findallbyre('((?:[^,\(]|\([^\(\)]*\))*)', part)
                for subpart in subparts:
                    if '(' in subpart:
                        result += [(lang.strip(), subpart[:subpart.find('(')]) for lang in self.findbyre('\(.*?)\)', subpart).split(',')]
                    else:
                        result.append(('nl', subpart))
        section = self.findbyre('Aliassen:(.*)', html)
        if section:
            parts = self.findallbyre('(<span.*?/span>', section)
            for part in parts:
                result += [(language.strip(), self.findbyre('>([^<>]*)</span>', part)) for language in self.findbyre('<span title="(.*?)">', part).split(',')]
        return result
                
    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html)


class HdsAnalyzer(Analyzer):
    def setup(self):
        self.id = "%06i"%int(self.id)
        self.dbproperty = "P902"
        self.dbid = "Q642074"
        self.dbname = "Historical Dictionary of Switzerland"
        self.urlbase = "https://hls-dhs-dss.ch/de/articles/{id}/"
        self.hrtre = '(<h1.*?<!-- noindex -->)'
        self.language = 'de'
        self.escapeunicode = True

    def finddescription(self, html):
        return self.findbyre('property="og:description" content="(.*?)"', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)(<h1.*?<!-- noindex -->)', html)
                
    def findnames(self, html):
        return [self.findbyre('(?s)<title>(.*?)<', html)]

    def findfirstname(self, html):
        return self.findbyre('<span itemprop="givenName">(.*?)</span>', html, 'firstname')

    def findlastname(self, html):
        return self.findbyre('<span itemprop="familyName">(.*?)</span>', html, 'lastname')

    def findbirthdate(self, html):
        return self.findbyre('<span itemprop="birthDate">(.*?)</span>', html)

    def finddeathdate(self, html):
        return self.findbyre('<span itemprop="deathDate">(.*?)</span>', html)

    def findbirthplace(self, html):
        return self.findbyre('<img alt="geboren"[^<>]*>\s*[^\s]*\s*([\w\s-]*)', html, 'city')
    
    def finddeathplace(self, html):
        return self.findbyre('<img alt="gestorben"[^<>]*>\s*[^\s]*\s*([\w\s-]*)', html, 'city')

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html, includesocial=False)


class NtaAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P1006"
        self.dbid = None
        self.dbname = "NTA"
        self.urlbase = "http://data.bibliotheken.nl/doc/thes/p{id}"
        self.hrtre = '(<h1.*?)<div id="bnodes">'
        self.language = 'nl'

    def finddescription(self, html):
        return self.findbyre('<h1><span>(.*?)<', html)

    def findnames(self, html):
        result = [self.findbyre('(?s)<title>(.*?)<', html)]
        section = self.findbyre('(?s)alternateName</span>(.*?)<label', html)
        if section:
            result += self.findallbyre('(?s)<div class="fixed">(.*?)[&<]', html)
        return result

    def findinstanceof(self, html):
        return self.findbyre('http://schema.org/(.*?)[&"\']', html, 'instanceof')

    def finddeathdate(self, html):
        return self.findbyre('(?s)<span>deathDate</span>.*?<span.*?>(.*?)[&<]', html)

    def findbirthdate(self, html):
        return self.findbyre('(?s)<span>birthDate</span>.*?<span.*?>(.*?)[&<]', html)

    def findfirstname(self, html):
         return self.findbyre('(?s)<span>givenName</span>.*?<span.*?>(.*?)[&<]', html, 'firstname')
       
    def findlastname(self, html):
         return self.findbyre('(?s)<span>familyName</span>.*?<span.*?>(.*?)[&<]', html, 'lastname')

    def findviaf(self, html):
        return self.findbyre('http://viaf.org/viaf/(\d+)', html)


class PtbnpAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P1005"
        self.dbid = None
        self.dbname = "Biblioteca Nacional de Portugal"
        self.urlbase = "http://urn.bn.pt/nca/unimarc-authorities/txt?id={id}"
        self.hrtre = '(.*)'
        self.language = 'pt'
        self.escapehtml = True

    def findnames(self, html):
        changedhtml = self.TAGRE.sub(' ', html).replace('$b', ' ')
        return self.findallbyre('[24]00.*\$a(.*?)\$', changedhtml)

    def finddescription(self, html):
        return self.findbyre('>830<.*?\$a.*?</font>([^<>]*)', html)

    def findnationality(self, html):
        return self.findbyre('>102<.*?\$a(?:<[^<>]*>)*([^<>]+)', html, 'country')

    def findlongtext(self, html):
        return '\n'.join(self.findallbyre('>830<.*?\$a.*?</font>([^<>]*)', html))

    def findbirthdate(self, html):
        result = self.findbyre('>200<.*?\$f.*?</font>([^<>]*)-', html)
        if result and "ca " not in result and "fl." not in result: return result

    def finddeathdate(self, html):
        result = self.findbyre('>200<.*?\$f.*?</font>[^<>]*-([^<>,]*)', html)
        if result and "ca " not in result and "fl." not in result:
            return result


class BibsysAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P1015"
        self.dbid = None
        self.dbname = "BIBSYS"
        self.urlbase = "https://authority.bibsys.no/authority/rest/authorities/html/{id}"
        self.hrtre = '(<body>.*)'
        self.language = 'en'

    def findnames(self, html):
        return self.findallbyre('<td>[^<>]*name[^<>]*</td><td>([^<>]*)</td>', html)

    def findinstanceof(self, html):
        return self.findbyre('<td>Authority type</td><td>(.*?)</td>', html, 'instanceof')

    def findisni(self, html):
        return self.findbyre('<td>isni</td><td>(.*?)</td>', html)

    def findviaf(self, html):
        return self.findbyre('http://viaf.org/viaf/(\w+)', html) or\
               self.findbyre('<td>viaf</td><td>(.*?)</td>', html)
        
    def findfirstname(self, html):
        return self.findbyre('<td>Personal name</td><td>[^<>]*,\s*(\w+)', html, 'firstname')

    def findlastname(self, html):
        return self.findbyre('<td>Personal name</td><td>([^<>]*),', html, 'lastname')

    def findbirthdate(self, html):
        return self.findbyre('<td>Dates associated with a name</td><td>([^<>]*)-', html)

    def finddeathdate(self, html):
        return self.findbyre('<td>Dates associated with a name</td><td>[^<>]*-([^<>]*)', html)


class KunstindeksAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P1138'
        self.dbid = 'Q3362041'
        self.dbname = 'Kunstindeks Danmark'
        self.urlbase = 'https://www.kulturarv.dk/kid/VisKunstner.do?kunstnerId={id}'
        self.urlbase3 = 'https://www.kulturarv.dk/kid/SoegKunstnerVaerker.do?kunstnerId={id}&hitsPerPage=1000'
        self.hrtre = 'Information from Kunstindeks Danmark</h2>(.*?)</table>'
        self.language = 'da'

    def findnames(self, html):
        return [
            self.findbyre(':([^<>]*)</h1>', html),
            self.findbyre('Name:\s*</b>(.*?)<', html)
            ]

    def findlongtext(self, html):
        return self.findbyre('(?s)(<h1>.*?)<td class="right\d', html)

    def findlastname(self, html):
        return self.findbyre('(?s)<b>Name: </b>([^<>]*),', html, 'lastname')

    def findfirstname(self, html):
        return self.findbyre('(?s)<b>Name: </b>[^<>]*,\s*(\w+)', html, 'firstname')

    def findbirthplace(self, html):
        return self.findbyre('(?s)<b>Born: </b>([^<>]*),', html, 'city')

    def findbirthdate(self, html):
        return self.findbyre('(?s)<b>Born: </b>[^<>]*?([\d\-]+)\s*<', html)
    
    def finddeathplace(self, html):
        return self.findbyre('(?s)<b>Died: </b>([^<>]*),', html, 'city')

    def finddeathdate(self, html):
        return self.findbyre('(?s)<b>Died: </b>[^<>]*?([\d\-]+)\s*<', html)

    def findoccupations(self, html):
        section = self.findbyre('(?s)Occupation: </b>(.*?)<', html)
        if section:
            return self.findallbyre('([\s\w]+)', section, 'occupation')

    def findgender(self, html):
        return self.findbyre('(?s)Sex: </b>(.*?)<', html, 'gender')

    def findnationality(self, html):
        return self.findbyre('(?s)Nationality: </b>(.*?)<', html, 'country')

    def findincollections(self, html):
        return self.findallbyre('museumId=[^<>]*>(.*?)<', html, 'museum')
    
    

class IaafAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P1146'
        self.dbid = None
        self.dbname = 'IAAF'
        self.urlbase = 'https://www.iaaf.org/athletes/athlete={id}'
        self.hrtre = '(<div class="row offset.*? <div class="clearfix">)'
        self.language = 'en'

    def findnames(self, html):
        return [self.findbyre('(?s)<h1>(.*?)<', html)]

    def findlongtext(self, html):
        return self.findbyre('(?s)<div class="modal-body athletepopup">(.*?)</script>', html)

    def instanceof (self, html):
        return 'Q5'
    
    def findoccupations(self, html):
        return ['Q11513337']

    def findsports(self, html):
        return ['Q542']

    def findnationality(self, html):
        return self.findbyre('(?s)COUNTRY.*?>([^<>]*)</span>', html, 'country')

    def findbirthdate(self, html):
        return self.findbyre('(?s)DATE OF BIRTH\s*<br\s*/>(.*?)<', html)


class ScopusAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P1153'
        self.dbid = 'Q371467'
        self.dbname = 'Scopus'
        self.urlbase = 'https://www.scopus.com/authid/detail.uri?authorId={id}'
        self.hrtre = '(<h2.*?)<h4'
        self.language = 'en'

    def findinstanceof(self, html):
        return 'Q5'

    def findnames(self, html):
        result = self.findallbyre('name="authorPreferredName" value="(.*?)"', html)
        section = self.findbyre('(?s)(<div id="otherNameFormatBadges".*?</div>)', html)
        if section:
            result += self.findallbyre('>(.*?)<', section)
        return result

    def findworkfields(self, html):
        section = self.findbyre('(?s)(<div id="subjectAreaBadges".*?</div>)', html)
        if section:
            return self.findallbyre('>(.*?)<', section, 'subject')

    def findmixedrefs(self, html):
        return self.defaultmixedrefs(html)

    def findemployers(self, html):
        section = self.findbyre('(?s)<div class="authAffilcityCounty">(.*?)</div>', html)
        if section:
            return self.findallbyre('>([^<>]*)</span>', section, 'employer', alt=['university'])

    def findworkplaces(self, html):
        section = self.findbyre('(?s)<div class="authAffilcityCounty">(.*?)</div>', html)
        if section:
            return self.findallbyre('(?s)>,([^<>],[^<>]*)<', section.replace('\n', ' '), 'city')


class RodovidAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P1185'
        self.dbid = 'Q649227'
        self.dbname = 'Rodovid'
        self.urlbase = 'https://en.rodovid.org/wk/Person:{id}'
        self.hrtre = '<table class="persondata">(.*?<h2>.*?)<h2'
        self.language = 'en'
        self.escapehtml = True

    def findnames(self, html):
        return [
            self.findbyre('<title>(.*?)(?: [bd]\. |<)', html),
            self.findbyre('<h1[^<>]*>(.*?)(?: [bd]\. |<)', html),
            self.findbyre('(?s)<b>Full name[^<>]*</b>\s*</td><td>(.*?)<', html)
            ]

    def findlongtext(self, html):
        return self.findbyre('(?s)<span class="mw-headline">Notes</span></h2>\s*<p>(.*?)<h\d', html)

    def findbirthdate(self, html):
        section = self.findbyre('(?s)Events</span></h2>(.*?)<h2', html)
        return self.findbyre('<b>([^<>]*)</b>birth:', section)

    def findbirthplace(self, html):
        section = self.findbyre('(?s)Events</span></h2>(.*?)<h2', html)
        return self.findbyre('>birth: <[^<>]*>(.*?)<', section, 'city')

    def finddeathdate(self, html):
        section = self.findbyre('(?s)Events</span></h2>(.*?)<h2', html)
        return self.findbyre('<b>([^<>]*)</b>death:', section)

    def finddeathplace(self, html):
        section = self.findbyre('(?s)Events</span></h2>(.*?)<h2', html)
        return self.findbyre('death: <[^<>]*>(.*?)<', section, 'city')

    def findchildren(self, html):
        section = self.findbyre('(?s)Events</span></h2>(.*?)<h2', html)
        return self.findallbyre("child birth:.*?Person:\d+'>(.*?)<", section, 'person')

    def findspouses(self, html):
        section = self.findbyre('(?s)Events</span></h2>(.*?)<h2', html)
        return self.findallbyre("marriage</a>.*?Person:\d+'>(.*?)<", section, 'person')

    def findfamily(self, html):
        section = self.findbyre('(?s)<b>Lineage\s*</b>(.*?)</tr>', html)
        if section:
            return self.findbyre('>([^<>]*)</a>', section, 'family')

    def findgender(self, html):
        return self.findbyre('(?s)Sex\s*</b>\s*</td><td>(.*?)<', html, 'gender')

    def findfather(self, html):
        section = self.findbyre('(?s)<b>Parents</b>(.*?)</tr>', html)
        if section:
            return self.findbyre("♂.*?Person:\d+'>(.*?)<", section, 'person')
        
    def findmother(self, html):
        section = self.findbyre('(?s)<b>Parents</b>(.*?)</tr>', html)
        if section:
            return self.findbyre("♀.*?Person:\d+'>(.*?)<", section, 'person')

    def findreligions(self, html):
        return self.findallbyre('(?s)religion:\s*<.*?>([^<>]+)<.*?></p>', html, 'religion')
    
    def findtitles(self, html):
        section = self.findbyre('(?s)Events</span></h2>(.*?)<h2', html)
        return self.findallbyre('title:.*?<a[^<>]*>(.*?)<', section, 'title')

 
class IbdbAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P1220'
        self.dbid = 'Q31964'
        self.dbname = 'IBDB'
        self.urlbase = 'https://www.ibdb.com/person.php?id={id}'
        self.hrtre = '(<h1>.*?)<div class="dottedLine">'
        self.language = 'en'

    def finddescription(self, html):
        return self.findbyre('<meta name="description" content="(.*?)"', html)

    def findnames(self, html):
        section = self.findbyre('(?s)<b>Also Known As</b>\s*</div>\s*<div[^<>]*>(.*?)</div>', html)
        if section:
            result = self.findallbyre('([^\[\]<>]*?)[\[<]', section)
        else:
            result = []
        return result + [
            self.findbyre('<title>([^<>]*?) – ', html)
            ]

    def findlongtext(self, html):
        parts = self.findallbyre('"personDescription"[^<>]*>(.*?)<', html)
        if parts:
            return ' '.join(parts)

    def findoccupations(self, html):
        section = self.findbyre('(?s)<div class="s12 wrapper tag-block-compact extramarg">(.*?)</div>', html)
        if section:
            return self.findallbyre('>([^<>]*)<', section, 'occupation')

    def findbirthdate(self, html):
        return self.findbyre('(?s)<div class="xt-lable">Born</div>\s*<div class="xt-main-title">(.*?)</div>', html)

    def findbirthplace(self, html):
        return self.findbyre('(?s)<div class="xt-lable">Born</div>\s*<div class="xt-main-title">[^<>]*</div>\s*<div class="xt-main-moreinfo">(.*?)</div>', html, 'city')
    
    def finddeathdate(self, html):
        return self.findbyre('(?s)<div class="xt-lable">Died</div>\s*<div class="xt-main-title">(.*?)</div>', html)

    def finddeathplace(self, html):
        return self.findbyre('(?s)<div class="xt-lable">Died</div>\s*<div class="xt-main-title">[^<>]*</div>\s*<div class="xt-main-moreinfo">(.*?)</div>', html, 'city')

    def findgender(self, html):
        return self.findbyre('(?s)<div class="xt-lable">Gender</div>\s*<div class="xt-main-title">(.*?)</div>', html, 'gender')

    def findawards(self, html):
        section = self.findbyre('(?s)<div id="awards".*?>(.*?)</table>', html)
        if section:
            parts = self.findallbyre('(?s)(<tr><th.*?</tr>\s*<tr>.*?</tr>)', section)
            result = []
            for part in parts:
                if not '[nominee]' in part:
                    result.append(self.findbyre('<th[^<>]*>(.*?)<', section, 'award'))
            return result

    def findnominations(self, html):
        section = self.findbyre('(?s)<div id="awards".*?>(.*?)</table>', html)
        if section:
            parts = self.findallbyre('(?s)(<tr><th.*?</tr>\s*<tr>.*?</tr>)', section)
            result = []
            for part in parts:
                if '[nominee]' in part:
                    result.append(self.findbyre('<th[^<>]*>(.*?)<', section, 'award'))
            return result

    def findspouses(self, html):
        return self.findallbyre('(?s)(?:Wife|Husband) of(?:<[^<>]*>|\s)*(.*?)<', html, 'person')
    
    def findpartners(self, html):
        return self.findallbyre('(?s)Partner of(?:<[^<>]*>|\s)*(.*?)<', html, 'person')
    

class IsfdbAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P1233"
        self.dbid = "Q2629164"
        self.dbname = "Internet Speculative Fiction Database"
        self.urlbase = "http://www.isfdb.org/cgi-bin/ea.cgi?{id}"
        self.hrtre = '<div class="ContentBox">(.*?)<div class="ContentBox">'
        self.language = 'en'
        self.escapeunicode = True

    def prepare(self, html):
        return html.replace('\\n', '\n')

    def findnames(self, html):
        return self.findallbyre('(?s)<b>Author:</b>(.*?)<', html) +\
               self.findallbyre('(?s)Name:</b>(.*?)<', html) +\
               self.findallbyre('dir="ltr">(.*?)<', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)<div class="ContentBox">(.*?)<div class="ContentBox">', html)
    
    def findinstanceof(self, html):
        return "Q5"

    def findfirstname(self, html):
        return self.findbyre('(?s)Legal Name:</b>[^<>]+,\s*(\w+)', html, 'firstname')

    def findlastname(self, html):
        return self.findbyre('(?s)Legal Name:</b>([^<>]*),', html, 'lastname')

    def findbirthplace(self, html):
        return self.findbyre('(?s)Birthplace:</b>(.*?)<', html, 'city')

    def finddeathplace(self, html):
        return self.findbyre('(?s)Deathplace:</b>(.*?)<', html, 'city')

    def findbirthdate(self, html):
        return self.findbyre('(?s)Birthdate:</b>(.*?)<', html)

    def finddeathdate(self, html):
        return self.findbyre('(?s)Deathdate:</b>(.*?)<', html)

    def findlanguagesspoken(self, html):
        section = self.findbyre('(?s)Language:</b>(.*?)<', html)
        if section:
            return self.findallbyre('(\w+)', section, 'language')

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html)

    def findgenres(self, html):
        section = self.findbyre('(?s)Author Tags:</b>(.*?)<(?:/ul|li)', html)
        if section:
            return self.findallbyre('>(.*?)<', section, 'genre')


class NndbAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P1263"
        self.dbid = "Q1373513"
        self.dbname = "NNDB"
        self.urlbase = 'https://www.nndb.com/people/{id}/'
        self.hrtre = '(<font size=\+3.*?)<font size=-1>'
        self.language = 'en'

    def getvalue(self, field, dtype=None, bold=True):
        rawtext = self.findbyre('%s%s:%s\s*(.+?)<(?:br|p)>'%('<b>' if bold else ' ',field, '</b>' if bold else ''), self.html)
        if rawtext:
            text = self.TAGRE.sub('', rawtext)
            return self.findbyre('(.+)', text, dtype)

    def getvalues(self, field, dtype=None, bold=True):
        rawtexts = self.findallbyre('%s%s:%s\s*(.+?)<(?:br|p)>'%('<b>' if bold else ' ',field, '</b>' if bold else ''), self.html)
        texts = [self.TAGRE.sub('', rawtext) for rawtext in rawtexts]
        return [self.findbyre('(.+)', text, dtype) for text in texts]

    def findinstanceof(self, html):
        return 'Q5'

    def finddescription(self, html):
        return self.getvalue('Executive summary')

    def findnames(self, html):
        return [
            self.findbyre('<title>(.*?)<', html),
            self.findbyre('<font size=\+3.*?>\s*<b>(.*?)<', html),
            self.getvalue('AKA'),
            ]

    def findbirthdate(self, html):
        return (self.getvalue('Born') or '').replace('-', ' ')

    def finddeathdate(self, html):
        return (self.getvalue('Died') or '').replace('-', ' ')
    
    def findbirthplace(self, html):
        return self.getvalue('Birthplace', 'city')
    
    def finddeathplace(self, html):
        return self.getvalue('Location of death', 'city')

    def findcausedeath(self, html):
        return self.getvalue('Cause of death', 'causedeath')
    
    def findmannerdeath(self, html):
        return self.getvalue('Cause of death', 'mannerdeath')

    def findgender(self, html):
        return self.getvalue('Gender', 'gender')

    def findethnicity(self, html):
        return self.getvalue('Race or Ethnicity', 'ethnicity')

    def findoccupations(self, html):
        result = self.getvalue('Occupation')
        if result:
            return self.findallbyre('([\w\s]+)', result, 'occupation')

    def findnationality(self, html):
        return self.getvalue('Nationality', 'country')

    def findspouses(self, html):
        return self.getvalues('Wife', 'person') + self.getvalues('Husband', 'person')

    def findfather(self, html):
        return self.getvalue('Father', 'person')

    def findmother(self, html):
        return self.getvalue('Mother', 'person')

    def findsiblings(self, html):
        return self.getvalues('Brother', 'person') + self.getvalues('Sister', 'person')

    def findchildren(self, html):
        return self.getvalues('Son', 'person') + self.getvalues('Daughter', 'person')

    def findorientation(self, html):
        return self.getvalue('Sexual orientation', 'orientation')

    def findschools(self, html):
        return self.getvalues('High School', 'university', bold=False) +\
               self.getvalues('University', 'university', bold=False)

    def findemployers(self, html):
        return self.getvalues('Teacher', 'employer', bold=False) +\
               self.getvalues('Professor', 'employer', bold=False)

    def findresidence(self, html):
        return self.findbyre('Resides in ([^<>]+)', html, 'city')

    def findwebsite(self, html):
        return self.getvalue('Official Website')
    

class ConorAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P1280"
        self.dbid = "Q16744133"
        self.dbname = "CONOR.SI"
        self.urlbase = "https://plus.cobiss.si/opac7/conor/{id}"
        self.hrtre = '(<table[^<>]*table-striped.*?</table>)'
        self.language = 'sl'

    def finddescription(self, html):
        return self.findbyre('<h3 class="page-title">(.*?)<', html)

    def findnames(self, html):
        result = [self.findbyre('"page-title">(.*?)[\{<]', html)]
        result = [','.join(r.split(',')[:2]) for r in result if r]
        return result

    def findnationality(self, html):
        return self.findbyre('(?s)<td>Dr[^<>]*ava</td>\s*<td>(.*?)[\(<]', html, 'country')

    def findlanguagesspoken(self, html):
        section = self.findbyre('(?s)<td>Jezik[^<>]*</td>\s*<td>(.*?)</td>', html)
        if section:
            return self.findallbyre('([^\(\);]+)\(', section, 'language')

    def findinstanceof(self, html):
        return "Q5"

    def findlastname(self, html):
        return self.findbyre('(?s)<td>Osebno ime</td>.*?<a[^<>]*>([^<>]*?),', html, 'lastname')

    def findfirstname(self, html):
        return self.findbyre('(?s)<td>Osebno ime</td>.*?<a[^<>]*>[^<>,]*,\s*(\w+)', html, 'firstname')

    def findbirthdate(self, html):
        return self.findbyre('(?s)<td>Osebno ime</td>.*?<a[^<>]*>[^<>]*,([^<>,]*)-', html)

    def finddeathdate(self, html):
        return self.findbyre('(?s)<td>Osebno ime</td>.*?<a[^<>]*>[^<>]*-([^<>]*?)<', html)

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html)


class MunzingerAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P1284'
        self.dbid = 'Q974352'
        self.dbname = 'Munzinger'
        self.urlbase = 'https://www.munzinger.de/search/go/document.jsp?id={id}'
        self.hrtre = '<div class="content">(.*?)<div class="mitte-text">'
        self.language = 'de'

    def findinstanceof(self, html):
        return 'Q5'

    def findnames(self, html):
        return [
            self.findbyre('(?s)<title>([^<>]*) - ', html),
            self.findbyre('<h1>(.*?)</h1>', html)
            ]

    def finddescriptions(self, html):
        return [
            self.findbyre('(?s)</h1>(.*?)<', html),
            self.findbyre('"description" content="[^<>"]*:(.*?)"', html)
            ]

    def findlongtext(self, html):
        return self.findbyre('(?s)(<h2 id=".*)<br style="clear:both;"', html)

    def findoccupations(self, html):
        section = self.findbyre('(?s)</h1>(.*?)<', html)
        if section:
            return self.findallbyre('([^;]*)', section, 'occupation', skips=['degree'])

    def findbirthdate(self, html):
        return self.findbyre('(?s)Geburtstag:(?:<[^<>]*>|\s)*((?:\d+\. \w+)? \d{3,4})', html)

    def findbirthplace(self, html):
        return self.findbyre('(?s)Geburtstag:(?:<[^<>]*>|\s)*(?:\d+\. \w+)? \d{3,4} ([^<>]*)', html, 'city')
    
    def finddeathdate(self, html):
        return self.findbyre('(?s)Todestag:(?:<[^<>]*>|\s)*((?:\d+\. \w+)? \d{3,4})', html)

    def finddeathplace(self, html):
        return self.findbyre('(?s)Todestag:(?:<[^<>]*>|\s)*(?:\d+\. \w+)? \d{3,4} ([^<>]*)', html, 'city')
    
    def findnationality(self, html):
        return self.findbyre('(?s)Nation:(?:<[^<>]*>|\s)*([^<>]*)', html, 'country')

    

class PeopleAustraliaAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P1315"
        self.dbid = None
        self.dbname = "National Library of Australia"
        self.urlbase = "https://trove.nla.gov.au/people/{id}"
        self.hrtre = '(<h1.*?)<h2>(?:Resources|Related)'
        self.language = 'en'
        self.escapeurl = True
        self.escapehtml = True

    def finddescriptions(self, html):
        return [
            self.findbyre('(?s)<h2>Biographies</h2>.*?<p>(.*?)<', html),
            self.findbyre('(?s)<dd class="creator">(.*)</dd>', html),
            ]

    def findnames(self, html):
        return [self.findbyre('(?s)<h1>(.*?)[\(<]', html)] +\
               self.findallbyre('(?s)othername">(.*?)[\<]', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)<h2>Biographies</h2>(.*?)<h2', html)

    def findbirthdate(self, html):
        return self.findbyre('(?s)<h1>[^<>]+\(([^<>\)]*)-', html)

    def finddeathdate(self, html):
        return self.findbyre('(?s)<h1>[^<>]+\([^<>\)]*-([^<>\)]*)\)', html)

    def findfirstname(self, html):
        return self.findbyre('(?s)<h1>[^<>,\(\)]+,\s*(\w+)', html, 'firstname')

    def findlastname(self, html):
        return self.findbyre('(?s)<h1>([^<>,\(\)]+),', html, 'lastname')
            
    def findoccupations(self, html):
        section = self.findbyre('(?s)<dt>Field of Activity</dt>(.*?)</dd>', html)
        if section:
            return self.findallbyre('>([^<>]+)</a>', section, 'occupation')

    def findmixedrefs(self, html):
        return [x for x in self.finddefaultmixedrefs(html, includesocial=False) if not (x[0] == 'P345' and not x[1].startswith('nm'))]

    def findschools(self, html):
        return self.findallbyre('(?s)\(student\)\s*<[^<>]*>(.*?)<', html, 'university')

    def findemployers(self, html):
        return self.findallbyre('(?s)\(employee\)\s*<[^<>]*>(.*?)<', html, 'employer', alt=['university'])

    def findworkfields(self, html):
        section = self.findbyre('(?s)<dt>Field of activity</dt>\s*<dd>(.*?)</dd>', html)
        if section:
            return self.findallbyre('(?s)>(.*?)<', section, 'subject')


class ArtUkAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P1367'
        self.dbid = None
        self.dbname = 'Art UK'
        self.urlbase = 'https://artuk.org/discover/artists/{id}'
        self.hrtre = '<div class="page-header">(.*?)<main id="main">'
        self.language = 'en'

    def findnames(self, html):
        return self.findallbyre('(?s)<h2>(.*?)<', html)

    def findbirthdate(self, html):
        return self.findbyre('(?s)</h2>\s*<p>([^<>]*)–', html)

    def finddeathdate(self, html):
        return self.findbyre('(?s)</h2>\s*<p>[^<>]*–([^<>]*)', html)

    def findnationalities(self, html):
        section = self.findbyre('(?s)>([^<>]+)</p>\s*</div>\s*<!-- END: skins/artuk/actor/v_page_title -->', html)
        if section:
            return self.findallbyre('([^,]+)', section, 'country')

    def findincollections(self, html):
        return self.findallbyre('(?s)<a href="https://artuk.org/visit/venues/[^"]*" title="(.*?)"', html, 'museum')
        

class LnbAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P1368'
        self.dbid = None
        self.dbname = 'National Library of Latvia'
        self.urlbase = 'https://kopkatalogs.lv/F?func=direct&local_base=lnc10&doc_number={id}'
        self.hrtre = '<!-- filename: full-999-body -->(.*)<!-- filename: direct-tail  -->'
        self.escapehtml = True
        self.language = 'lv'

    def prepare(self, html):
        return html.replace('&nbsp;', ' ')

    def getvalue(self, field, html, dtype=None, alt=None):
        return self.findbyre('(?s)<td[^<>]*>[^<>]*%s[^<>]*</td>\s*<td[^<>]*>(.*?)</td>'%field, html, dtype, alt=alt)

    def getvalues(self, field, html, dtype=None, alt=None):
        parts = re.findall('(?s)<td[^<>]*>(.*?)</td>', html)
        status = 'inactive'
        result = []
        for part in parts:
            if status == 'active':
                result.append(self.findbyre('(?s)(.*)', part.strip().rstrip('.'), dtype, alt=alt))
                status = 'waiting'
            elif field in part:
                status = 'active'
            elif status == 'waiting' and not part.strip():
                status = 'active'
            else:
                status = 'inactive'
        return result

    def instanceof(self, html):
        return self.getvalue('Entītes veids', html, 'instanceof')

    def findnames(self, html):
        namecontainers = self.getvalues('Persona', html) + self.getvalues('Norāde', html)
        namecontainers = [self.TAGRE.sub('', namecontainer) for namecontainer in namecontainers]
        return [self.findbyre('([^\d]+),', namecontainer) for namecontainer in namecontainers] +\
               [self.findbyre('([^\d]+)', namecontainer) for namecontainer in namecontainers]

    def findbirthplace(self, html):
        return self.findbyre('Dzim\.:([^<>]*)\.', html, 'city')

    def finddeathplace(self, html):
        return self.findbyre('Mir\.:([^<>]*)\.', html, 'city')

    def findworkfields(self, html):
        return self.getvalues('Darbības joma', html, 'subject')

    def findoccupations(self, html):
        return self.getvalues('Nodarb', html, 'occupation')

    def findgender(self, html):
        return self.getvalue('Dzimums', html, 'gender')

    def findisni(self, html):
        return self.getvalue('ISNI', html)

    def findviaf(self, html):
        return self.findbyre('\(VIAF\)\s*(\d+)', html)

    def findemployers(self, html):
        return self.getvalues('Grupa saistīta ar', html, 'employer', alt=['university'])

    def findlanguagesspoken(self, html):
        if self.instanceof(html) == 'Q5':
            return self.getvalues('Valoda saistīta ar', html, 'language')


class OxfordAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P1415'
        self.dbid = 'Q17565097'
        self.dbname = 'Oxford Dictionary of National Biography'
        self.urlbase = 'https://doi.org/10.1093/ref:odnb/{id}'
        self.hrtre = '<div class="abstract">(.*?)</div>'
        self.language = 'en'

    def findnames(self, html):
        return [
            self.findbyre('"pf:contentName" : "(.*?)\(', html)
            ]


    def findoccupations(self, html):
        section = self.findbyre('"pf:contentName".*?\)(.*?)"', html)
        if section:
            parts = section.split(" and ")
            results = []
            for part in parts:
                results += self.findbyre('([\w\s]+)', part, 'occupation')
            return results

    def findbirthdate(self, html):
        return self.findbyre('<title>[^<>]*\((\d+)-', html)

    def finddeathdate(self, html):
        return self.findbyre('<title>[^<>]*-(\d+)\)', html)

    def findlongtext(self, html):
        return self.findbyre('<div class="abstract">(.*?)</div>', html)


class SandrartAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P1422'
        self.dbid = 'Q17298559'
        self.dbname = 'Sandrart'
        self.urlbase = 'http://ta.sandrart.net/en/person/view/{id}'
        self.hrtre = '<h2>Basic data</h2>(.*?)<h2>Occurrences'
        self.language = 'de'

    def findlongtext(self, html):
        return self.findbyre('(?s)<h2>Basic data</h2>.*?<p>(.*?)</p>', html)

    def findnames(self, html):
        return [self.findbyre('<h1>(.*?)<', html)]

    def finddescription(self, html):
        return self.findbyre('(?s)<h2>Basic data</h2>.*?<p>(.*?)(?:, geb\. |, gest\.|;|<)', html)

    def findbirthdate(self, html):
        return self.findbyre('geb\. (\d+)', html)

    def findbirthplace(self, html):
        return self.findbyre('geb\.[^;,<>]* in (?:<[^<>]*>)?(.+?)[,<]', html, 'city')

    def finddeathdate(self, html):
        return self.findbyre('gest\. (\d+)', html)

    def finddeathplace(self, html):
        return self.findbyre('gest\.[^;,<>]* in (?:<[^<>]*>)?(.+?)[,<]', html, 'city')

    def findoccupations(self, html):
        section = self.finddescription(html)
        if section:
            result = []
            parts = section.split(' und ')
            for part in parts:
                result += self.findallbyre('[\w\s]+', part, 'occupation')
            return result

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html, includesocial=False)


class FideAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P1440'
        self.dbid = 'Q27038151'
        self.dbname = 'FIDE'
        self.urlbase = 'https://ratings.fide.com/card.phtml?event={id}'
        self.hrtre = '(<table width=480.*?</table>)'
        self.language = 'en'
        self.escapehtml = True

    def findinstanceof(self, html):
        return 'Q5'

    def findnames(self, html):
        return [ self.findbyre('<td bgcolor=#efefef width=230 height=20>(.*?)<', html) ]

    def findnationality(self, html):
        return self.findbyre('Federation</td><td[^<>]*>(.*?)<', html, 'country')

    def findchesstitle(self, html):
        return self.findbyre('FIDE title</td><td[^<>]*>(.*?)<', html, 'chesstitle')

    def findgender(self, html):
        return self.findbyre('Sex</td><td[^<>]*>(.*?)<', html, 'gender')

    def findbirthdate(self, html):
        return self.findbyre('B-Year</td><td[^<>]*>(.*?)<', html)

    def findoccupations(self, html):
        return ['Q10873124']

    

class SportsReferenceAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P1447'
        self.dbid = 'Q18002875'
        self.dbname = 'sports-reference.com'
        self.urlbase = 'https://www.sports-reference.com/olympics/athletes/{id}.html'
        self.hrtre = '(<h1.*?</div>)'
        self.language = 'en'

    def findnames(self, html):
        return [
            self.findbyre('<h1.*?>(.*?)<', html),
            self.findbyre('Full name:</span>([^<>]*)', html),
            ]

    def findlongtext(self, html):
        return self.findbyre('(?s)<h2[^<>]*>Biography</h2>(.*?)<h2', html)

    def findinstanceof(self, html):
        return "Q5"

    def findgender(self, html):
        return self.findbyre('Gender:</span>([^<>]*)', html, 'gender')

    def findheights(self, html):
        return [self.findbyre('Height:</span>[^<>]*\((.*?)\)', html)]

    def findweights(self, html):
        return [
            self.findbyre('Weight:</span>(.*?)\(', html),
            self.findbyre('Weight:</span>[^<>]*\((.*?)\)', html),
            ]

    def findbirthdate(self, html):
        return self.findbyre('data-birth="(.*?)"', html)

    def finddeathdate(self, html):
        return self.findbyre('data-death="(.*?)"', html)

    def findbirthplace(self, html):
        return self.findbyre('birthplaces\.cgi.*?">(.*?)<', html, 'city')

    def findsportteams(self, html):
        return [self.findbyre('Affiliations:</span>([^<>,]*)', html, 'club')]

    def findnationality(self, html):
        return self.findbyre('Country:</span>.*?>([^<>]*)</a>', html, 'country')

    def findsports(self, html):
        section = self.findbyre('(?s)Sport:</span>(.*?)(?:<p>|<br>|</div>)', html)
        if section:
            return self.findallbyre('>([^<>]*)</', section, 'sport')
    
    def findoccupations(self, html):
        section = self.findbyre('(?s)Sport:</span>(.*?)(?:<p>|<br>|</div>)', html)
        if section:
            return self.findallbyre('>([^<>]*)</', section, 'occupation')
        else:
            return ["Q2066131"]

    def findparticipations(self, html):
        section = self.findbyre('(?s)(<tbody>.*</tbody>)', html)
        if section:
            return self.findallbyre('<a href="/olympics/\w+/\d+/">(.*?)<', section, 'olympics')


class PrdlAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P1463"
        self.dbid = "Q7233488"
        self.dbname = "Post-Reformation Digital Library"
        self.urlbase = 'http://prdl.org/author_view.php?a_id={id}'
        self.hrtre = '(<span id="header_text">.*?</table>)'
        self.language = 'en'

    def findnames(self, html):
        return self.findallbyre('&ldquo;([^<>]*?)&rdquo;', html)

    def finddescription(self, html):
        result = self.findbyre('Academic Title</span>(<span.*?</span>)', html)
        if result:
            return self.TAGRE.sub('', result)

    def findinstanceof(self, html):
        return 'Q5'

    def findbirthdate(self, html):
        result = self.findbyre('</b></span><span[^<>]*>\s*\((?:c\.)?([^<>\-\)]*)', html)
        if result and 'fl.' not in result and re.search("1\d{3}", result):
            return result

    def finddeathdate(self, html):
        section = self.findbyre('</b></span><span[^<>]*>\s*\(([^<>\)]*-[^<>]*?)\)', html)
        if section and 'fl.' not in section and re.search("-.*1\d{3}", section):
            return self.findbyre('\-(?:c\.)?(.*)', section)

    def findreligions(self, html):
        section = self.findbyre('>Tradition</span>(.*?)<span', html)
        if section:
            return self.findallbyre('<a[^<>]*>(.*?)<', section, 'religion')

    def findmixedrefs(self, html):
        result = self.finddefaultmixedrefs(html, includesocial=False)


class FifaAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P1469'
        self.dbid = None
        self.dbname = 'FIFA'
        self.urlbase = 'https://static.fifa.com/fifa-tournaments/players-coaches/people={id}/index.html'
        self.hrtre = '<div class="fdh-wrap contentheader">(.*?)</div>'
        self.language = 'en'

    def getvalue(self, field, html, dtype=None):
        return self.findbyre('<meta name="%s" content="(.*?)"'%field, html, dtype)

    def findinstanceof(self, html):
        return 'Q5'

    def findnames(self, html):
        return [
            self.findbyre(' - ([^<>\-]+)</title>', html),
            self.getvalue('profile-webname', html),
            self.getvalue('profile-webnameALT', html),
            self.getvalue('profile-fullname', html),
            self.findbyre('<h1>(.*?)<', html)
            ]

    def findlastname(self, html):
        result = self.getvalue('profile-commonSurname', html)
        if result:
            return self.findbyre('([A-Z\s]*) ', result + ' ', 'lastname')

    def findnationality(self, html):
        return self.getvalue('profile-countryname', html, 'country') or\
               self.getvalue('profile-countrycode', html, 'country')

    def findgender(self, html):
        return self.getvalue('profile-gender', html, 'gender')

    def findbirthdate(self, html):
        result = self.getvalue('person-birthdate', html)
        if result:
            return result.split('T')[0]

    def findsports(self, html):
        return ['Q2736']
    

class ZbmathAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P1556'
        self.dbid = None
        self.dbname = 'ZbMath'
        self.urlbase = 'https://zbmath.org/authors/?q=ai:{id}'
        self.hrtre = '</h2>(.*?)<div class="indexed">'
        self.language = 'en'
        self.escapehtml = True

    def findnames(self, html):
        result = self.findallbyre('<h2>(.*?)<', html)
        section = self.findbyre('(?s)<td>Published as:</td>(.*?)</tr>', html)
        if section:
            result += self.findallbyre(':([^<>"]+)"', section)
        return result

    def findlongtext(self, html):
        return self.findbyre('(?s)(<h2>.*?)<div class="indexed">', html)

    def findawards(self, html):
        section = self.findbyre('(?s)<td>Awards:</td>(.*?)</tr>', html)
        if section:
            return self.findallbyre('title="(.*?)"', section, 'award')

    def findmixedrefs(self, html):
        return [
            ('P227', self.findbyre('title="([^"<>]+)">GND</a>', html)),
            ('P549', self.findbyre('title="([^"<>]+)">MGP</a>', html)),
            ('P1563', self.findbyre('title="([^"<>]+)">MacTutor</a>', html)),
            ('P2456', self.findbyre('title="([^"<>]+)">dblp</a>', html)),
            ('P4252', self.findbyre('title="([^"<>]+)">Math-Net.Ru</a>', html)),
            ] +\
            self.finddefaultmixedrefs(html, includesocial=False)

    def findworkfields(self, html):
        section = self.findbyre('(?s)<h4>Fields</h4>(.*?)</table>', html)
        if section:
            preresults = self.findallbyre('(?s)<tr>(.*?)</tr>', section.replace('&nbsp;', ' '))[:5]
            results = []
            for preresult in preresults:
                if int(self.findbyre('">(\d+)</a>', preresult) or 0) > 5:
                    results.append(self.findbyre('(?s)"Mathematics Subject Classification">(.*?)<', preresult, 'subject'))
            return results

    def findwebsite(self, html):
        return self.findbyre('(?s)<td>Homepage:</td>\s*<td><a[^<>]*>(.*?)<', html)
        

class UBarcelonaAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P1580"
        self.dbid = None
        self.dbname = "University of Barcelona authority control"
        self.urlbase = "http://www.bib.ub.edu/fileadmin/autoritats/permanent/{id}"
        self.hrtre = '(<h2.*?</table>)'
        self.language = 'ca'
        self.escapehtml = True

    def finddescriptions(self, html):
        return [
            self.findbyre('<h2>(.*?)<', html),
            self.findbyre("(?s)Nota hist[^<>]*rica(.*?)</tr>", html)
            ]

    def findnames(self, html):
        return [self.findbyre('(?s)<h2>([^<>]*)(?:, \d|<)', html)] +\
               self.findallbyre('(?s)Emprat per<.*?<i>(.*?)(?:, \d|<)', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)(<h2.*?</table>)', html)

    def findinstanceof(self, html):
        return "Q5"

    def findviaf(self, html):
        return self.findbyre("http://viaf.org/viaf/(\w+)", html)

    def findworkplaces(self, html):
        section = self.findbyre("(?s)Lloc d'activitat(.*?)</tr>", html)
        if section:
            return self.findallbyre("<td>([^<>,]*)", section, 'city')

    def findoccupations(self, html):
        section = self.findbyre("(?s)Ocupaci(.*?)</tr>", html) or\
                  self.findbyre("(?s)Nota hist[^<>]*rica(.*?)</tr>", html)
        if section:
            return self.findallbyre("<td>([^<>,]*)", section, 'occupation')

    def findgender(self, html):
        return self.findbyre("G&egrave;nere.*?<td>(.*?)</td>", html, 'gender')


class DialnetAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P1607'
        self.dbid = 'Q3025975'
        self.dbname = 'Dialnet'
        self.urlbase = 'https://dialnet.unirioja.es/servlet/autor?codigo={id}'
        self.hrtre = '(<div id="paginaDeAutor" class="textos">.*?)<!-- Inicio de las secciones de la obra del autor -->'
        self.language = 'es'

    def findinstanceof(self, html):
        return 'Q5'

    def findnames(self, html):
        return self.findallbyre('title" content="(.*?)"', html) +\
               self.findallbyre('<title>(.*?)(?: - |</)', html) +\
               self.findallbyre('(?s)<h2>(.*?)</h2>', html)

    def findfirstname(self, html):
        return self.findbyre('first_name" content="(.*?)"', html, 'firstname')

    def findlastname(self, html):
        return self.findbyre('last_name" content="(.*?)"', html, 'lastname')

    def findemployers(self, html):
        section = self.findbyre('(?s)<ul id="listaDeInstituciones">(.*?)</ul>', html)
        if section:
            return self.findallbyre('">(.*?)<', section, 'employer', alt=['university'])

    def findworkfields(self, html):
        section = self.findbyre('(?s)<ul id="listaDeAreasDeConocimiento">(.*?)</ul>', html)
        if section:
            return self.findallbyre('">(.*?)<', section, 'subject')

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html, includesocial=False)


class ClaraAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P1615'
        self.dbid = 'Q18558540'
        self.dbname = 'CLARA'
        self.urlbase = 'http://clara.nmwa.org/index.php?g=entity_detail&entity_id={id}'
        self.hrtre = '<div id="pageArea">(.*?)<div style="width: 600px;'
        self.language = 'en'

    def findnames(self, html):
        return [self.findbyre('(?s)<div class="title">(.*?)<', html)]

    def findlongtext(self, html):
        return self.findbyre('(?s)(<div id="pageArea">.*?)<div style="width: 600px; border: 1px solid #000000; padding: 5px;">', html)

    def findinstanceof(self, html):
        return 'Q5'

    def findgender(self, html):
        return 'Q6581072'

    def findbirthdate(self, html):
        return self.findbyre('(?s)<div class="lifespan">([^<>]+?)-', html)

    def finddeathdate(self, html):
        result = self.findbyre('(?s)<div class="lifespan">[^<>]+-([^<>]+)</div>', html)
        if result.strip() != 'present':
            return result

    def findnationality(self, html):
        return self.findbyre('(?s)<div class="detail_label">Nationality:</div>\s*<div class="detail_text">(.*?)<', html, 'country')

    def findoccupations(self, html):
        result = []
        section = self.findbyre('(?s)<div class="detail_label">Artistic Role\(s\):</div>\s*<div class="detail_text">(.*?)<', html)
        if section:
            result = result + self.findallbyre('([^,]*)', section, 'occupation')
        section = self.findbyre('(?s)<div class="detail_label">Other Occupation\(s\):</div>\s*<div class="detail_text">(.*?)<', html)
        if section:
            result = result + self.findallbyre('([^,]*)', section, 'occupation')
        return result

    def findresidences(self, html):
        section = self.findbyre('(?s)<div class="detail_label">Place\(s\) of Residence:</div>\s*<div class="detail_text">(.*?)<', html)
        if section:
            return self.findallbyre('([^,]*)', section, 'city')


class WelshBioAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P1648'
        self.dbid = 'Q5273977'
        self.dbname = "Dictionary of Welsh Biography"
        self.urlbase = 'https://biography.wales/article/{id}'
        self.hrtre = '<div class="col-lg py-3 px-3">(.*?)</div>'
        self.language = 'en'
        self.escapehtml = True

    def findnames(self, html):
        return [self.findbyre('<b>Name:</b>(.*?)<', html)]

    def finddescription(self, html):
        return self.findbyre('<h1>(.*?)<', html)

    def findlongtext(self, html):
        return self.findbyre('<div class="col-lg py-3 px-3">.*?</div>(.*?)<h2', html)

    def findlastname(self, html):
        return self.findbyre('<h1>([^<>\(\),]*),', html, 'lastname')

    def findfirstname(self, html):
        return self.findbyre('<h1>[^<>\(\)]*?([^<>\(\),]*)\(', html, 'firstname')
    
    def findinstanceof(self, html):
        return 'Q5'

    def findbirthdate(self, html):
        return self.findbyre('<b>Date of birth:</b>(.*?)<', html)

    def finddeathdate(self, html):
        return self.findbyre('<b>Date of death:</b>(.*?)<', html)

    def findspouses(self, html):
        return self.findallbyre('<b>Spouse:</b>(.*?)<', html, 'person')

    def findchildren(self, html):
        return self.findallbyre('<b>Child:</b>(.*?)<', html, 'person')

    def findgender(self, html):
        return self.findbyre('<b>Gender:</b>(.*?)<', html, 'gender')

    def findoccupations(self, html):
        return self.findallbyre('<b>Occupation:</b>(.*?)<', html, 'occupation')
    
    def findfather(self, html):
        for person in self.findallbyre('<b>Parent:</b>(.*?)<', html, 'male-person'):
            if person:
                return person
            
    def findmother(self, html):
        for person in self.findallbyre('<b>Parent:</b>(.*?)<', html, 'female-person'):
            if person:
                return person


class TgnAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P1667"
        self.dbid = "Q1520117"
        self.dbname = "Getty Thesaurus of Geographic Names"
        self.urlbase = "https://www.getty.edu/vow/TGNFullDisplay?find=&place=&nation=&subjectid={id}"
        self.hrtre = '(<TR>\s*<TD VALIGN=TOP>.+?)<!-- END PRINT -->'
        self.language = 'en'

    def finddescriptions(self, html):
        return [
            self.findbyre('<SPAN CLASS=page>.*?<B>(.*?)</B>', html),
            self.findbyre('<B>Note:.*?</B>(.*?)<', html),
            ]

    def findnames(self, html):
        section = self.findbyre('(?s)<B>Names:</B>(.*?)</TABLE>', html)
        if section:
            return self.findallbyre('<NOBR><B>(.*?)<', section)

    def findlongtext(self, html):
        return self.findbyre('(?s)<B>Note:\s*</B>(.*?)<', html)

    def findinstanceof(self, html):
        return self.findbyre('(?s)Place Types:.*?SPAN CLASS=page>(.*?)[<\(]', html, 'type')

    def findcountry(self, html):
        return self.findbyre('>([^<>]+)\s*</A>\s*\(nation\)', html, 'country')

    def findadminloc(self, html):
        county = self.findbyre('>([^<>]+)</A> \(county\)', html)
        state = self.findbyre('>([^<>]+)</A> \(state\)', html)
        if state:
            if county:
                return self.getdata('county', '{} county, {}'.format(county, state))
            else:
                return self.getdata('state', state)

    def findcoords(self, html):
        lat = self.findbyre('Lat:\s*(-?\d+\.\d+)', html)
        lon = self.findbyre('Long:\s*(-?\d+\.\d+)', html)
        if lat and lon:
            return '{} {}'.format(lat, lon)


class NlpAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P1695"
        self.dbid = None
        self.dbname = "National Library of Poland"
        self.urlbase = 'http://mak.bn.org.pl/cgi-bin/KHW/makwww.exe?BM=01&IM=04&NU=01&WI={id}'
        self.hrtre = '(<table.*?</table>)'
        self.language = 'pl'
        self.escapeunicode = True

    def finddescriptions(self, html):
        return self.findallbyre('>667.*?</I>(.*?)<', html)

    def findnames(self, html):
        return self.findallbyre('>1\..*?</I>(.*?)<', html)

    def findlongtext(self, html):
        return "\n".join(self.findallbyre('>667.*?</I>(.*?)<', html))

    def findoccupations(self, html):
        result = []
        sections = self.findallbyre('>667.*?</I>(.*?)<', html)
        for section in sections:
            result += self.findallbyre('([\s\w]+)', section, 'occupation')
        return result

    def findbirthdate(self, html):
        result = self.findbyre(' d </TT></I>\(([^<>]*)-', html)
        if result and not 'ca ' in result: return result

    def finddeathdate(self, html):
        result = self.findbyre(' d </TT></I>\([^<>]*-([^<>]*)\)', html)
        if result and not 'ca ' in result: return result

    def findnationality(self, html):
        for result in self.findallbyre('>667.*?</I>\s*([^\s<>]*)', html, 'country'):
            if result:
                return result


class DaaoAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P1707'
        self.dbid = 'Q5273961'
        self.dbname = 'DAAO'
        self.urlbase = 'https://www.daao.org.au/bio/{id}/'
        self.hrtre = '<div class="content_header research">(.*?)<!-- end content'
        self.language = 'en'
        self.escapehtml = True

    def getvalue(self, field, html, dtype=None):
        return self.findbyre('(?s)<dt>\s*%s\s*</dt>\s*<dd>(.*?)</dd>'%field, html, dtype)

    def findinstanceof(self, html):
        return 'Q5'

    def findnames(self, html):
        sections = self.findallbyre('(?s)<div class="aka">(.*?)<', html)
        result = []
        for section in sections:
            result += self.findallbyre('(?s)<li>(.*?)<', section)
        return self.findallbyre('<span class="name">(.*?)<', html) + result +\
               self.findallbyre('(/s)<dt>\s*Name\s*</dt>\s*<dd>(.*?)<', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)<div class="summary">(.*?)</div>', html)

    def finddescription(self, html):
        return self.findbyre('(?s)<div class="summary">(.*?)</div>', html)

    def findgender(self, html):
        return self.getvalue('Gender', html, 'gender')

    def findoccupations(self, html):
        result = []
        section = self.findbyre('(?s)<div class="roles">(.*?)</div>', html)
        if section:
            result += self.findallbyre('(?s)<li>(.*?),?\s*<', section, 'occupation')
        section = self.getvalue('Roles', html)
        if section:
            result += self.findallbyre('(?s)<li>(.*?)<', section, 'occupation')
        section = self.getvalue('Other Occupation', html)
        if section:
            result += self.findallbyre('(?s)<li>(.*?)[<\(]', section, 'occupation')
        return result

    def findbirthdate(self, html):
        return self.getvalue('Birth date', html)
       
    def findbirthplace(self, html):
        return self.getvalue('Birth place', html, 'city')

    def finddeathdate(self, html):
        return self.getvalue('Death date', html)
       
    def finddeathplace(self, html):
        return self.getvalue('Death place', html, 'city')

    def findresidences(self, html):
        section = self.getvalue('Residence', html)
        if section:
            return self.findallbyre('(?s)<li>[^<>]*?([^<>\d]+)</li>', section, 'city')

    def findlanguages(self, html):
        section = self.getvalue('Languages', html)
        if section:
            return self.findallbyre('(?s)<li>(.*?)<', section, 'language')



class GtaaAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P1741'
        self.dbid = 'Q19366588'
        self.dbname = 'GTAA'
        self.urlbase = 'http://data.beeldengeluid.nl/gtaa/{id}'
        self.hrtre = '<h3>DocumentationProperties</h3>(.*?)<h3'
        self.language = 'nl'

    def findlanguagenames(self, html):
        results = [
            ('nl', self.findbyre('<title>(.*?)<', html)),
            ('nl', self.findbyre('<h2>(.*?)<', html))
            ]
        section = self.findbyre('(?s)<h3>LexicalLabels</h3>(.*?)<h3', html)
        if section:
            results += re.findall('xml:lang="(\w+)">(.*?)<', section)
        return results

    def findlanguagedescriptions(self, html):
        section = self.findbyre('(?s)skos:scopeNote(.*?)<h3', html)
        if section:
            return re.findall('xml:lang="(\w+)">(.*?)<', section)

    def findlongtext(self, html):
        return self.findbyre('(?s)(<h3>DocumentationProperties</h3>.*?)<h3>Alternatieve formaten', html)
    
    def findoccupations(self, html):
        section = self.findbyre('(?s)skos:scopeNote(.*?)<h3', html)
        if section:
            results = []
            parts = self.findallbyre('(?s)">(.*?)<', section)
            for part in parts:
                results += self.findallbyre('([\w\s]+)', part, 'occupation')
            return results


class ParlementPolitiekAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P1749'
        self.dbid = 'Q14042250'
        self.dbname = 'Parlement & Politiek'
        self.urlbase = 'https://www.parlement.com/id/{id}'
        self.hrtre = '<p class="mnone">(.*?)</p>'
        self.language = 'nl'

    def getsection(self, field, html, ntype=None):
        return self.findbyre('(?s)%s</h2>\s*</div></div>(.*?)<[bp][>\s]'%field, html, ntype)

    def findlongtext(self, html):
        return self.findbyre('(?s)<p class="m(?:none|top)">(.*?)</div>', html)
    
    def findnames(self, html):
        return self.findallbyre('title" content="(.*?)"', html) +\
               self.findallbyre('<(?:title|h1)>(.*?)(?: - |<)', html)

    def finddescriptions(self, html):
        return self.findallbyre('[dD]escription" content="(.*?)"', html)

    def findfirstname(self, html):
        section = self.getsection('[vV]oorna[^<>]*', html)
        if section:
            return self.findbyre('\((.*?)\)', section, 'firstname') or\
                   self.findbyre('(\w+)', section, 'firstname')
        
    def findbirthplace(self, html):
        return self.findbyre('(?s)geboorteplaats en -datum</b><br>([^<>]*),', html, 'city')

    def findbirthdate(self, html):
        return self.findbyre('(?s)geboorteplaats en -datum</b><br>[^<>]*,([^<>]*)', html)
    
    def finddeathplace(self, html):
        return self.findbyre('(?s)overlijdensplaats en -datum</b><br>([^<>]*),', html, 'city')

    def finddeathdate(self, html):
        return self.findbyre('(?s)overlijdensplaats en -datum</b><br>[^<>]*,([^<>]*)', html)
    
    def findparties(self, html):
        section = self.findbyre('(?s)partij\(en\)</b><br>(.*?<)/div>', html)
        if section:
            return self.findallbyre('([^<>]+)<', section, 'party')
        
    def findpolitical(self, html):
        section = self.findbyre('(?s)stroming\(en\)</b><br>(.*?<)/div>', html)
        if section:
            return self.findallbyre('([^<>]+)<', section, 'politicalmovement')
        
    def findoccupations(self, html):
        section = self.getsection('(?s)Hoofdfuncties/beroepen[^<>]*', html)
        if section:
            return self.findallbyre('(?s)"opsomtekst">(.*?)[,<]', section, 'occupation')

    def findpositions(self, html):
        section = self.getsection('(?s)Hoofdfuncties/beroepen[^<>]*', html)
        if section:
            return self.findallbyre('(?s)"opsomtekst">(.*?)[,<]', section, 'position')

    def findemployers(self, html):
        section = self.getsection('(?s)Hoofdfuncties/beroepen[^<>]*', html)
        if section:
            return self.findallbyre('(?s)"opsomtekst">(.*?)[,<]', section, 'employer', alt=['university'])
        

class AmericanArtAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P1795'
        self.dbid = None
        self.dbname = 'Smithsonian American Art Museum'
        self.urlbase = 'https://americanart.si.edu/collections/search/artist/?id={id}'
        self.hrtre = '</h1>(.*?)<dt class="field--label visually-hidden">'
        self.language = 'en'

    def findnames(self, html):
        section = self.findallbyre('(?s)>Name</dt>(.*?)</dd>', html) +\
                  self.findallbyre('(?s)>Also Known as</dt>(.*?)</dd>', html)
        return self.findallbyre('(?s)>([^<>]+)<', '\n'.join(section))

    def findlongtext(self, html):
        return self.findbyre('(?s)</h1>(.*?)<dt class="field--label visually-hidden">', html)

    def findbirthplace(self, html):
        section = self.findbyre('(?s)Born</dt>.*?<span>(.*?)</span>', html)
        if section:
            return self.findbyre('(.*)', self.TAGRE.sub('', section).strip(), 'city')

    def finddeathplace(self, html):
        section = self.findbyre('(?s)Died</dt>.*?<span>(.*?)</span>', html)
        if section:
            return self.findbyre('(.*)', self.TAGRE.sub('', section).strip(), 'city')

    def findbirthdate(self, html):
        return self.findbyre('(?s)born[^<>\-]+?(\d+)\s*[\-<]', html)

    def finddeathdate(self, html):
        return self.findbyre('(?s)died[^<>]+?(\d+)\s*<', html)

    def findworkplaces(self, html):
        section = self.findbyre('(?s)Active in</dt>.*?<ul>(.*?)</ul>', html)
        if section:
            return self.findallbyre('(.*)', self.TAGRE.sub('', section), 'city')

    def findnationalities(self, html):
        section = self.findbyre('(?s)Nationalities</dt>(.*?)</dd>', html)
        if section:
            return self.findallbyre('>([^<>]+)<', section, 'country')

    def findincollections(self, html):
        return ['Q1192305']


class EmloAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P1802'
        self.dbid = 'Q44526767'
        self.dbname = 'Early Modern Letters Online'
        self.urlbase = 'http://emlo.bodleian.ox.ac.uk/profile/person/{id}'
        self.hrtre = '(<div id="details">.*?>)Catalogue Statistics</h3>'
        self.language = 'en'

    def findnames(self, html):
        result = self.findallbyre('<h2>([^<>]*),', html)
        section = self.findbyre('(?s)<dt>Alternative names</dt>\s*<dd>(.*?)</dd>', html)
        if section:
            result += self.findallbyre('([^<>;]+)', section)
        return result

    def finddescription(self, html):
        return self.findbyre('(?s)<dt>Titles or roles</dt>\s*<dd>(.*?)</dd>', html)

    def findlongtext(self, html):
        parts = [self.findbyre('(?s)<dt>Titles or roles</dt>\s*<dd>(.*?)</dd>', html) or ''] +\
                self.findallbyre('(?s)<div class="relations">(.*?)</div>', html)
        return '\n'.join(parts)

    def findoccupations(self, html):
        section = self.findbyre('(?s)<dt>Titles or roles</dt>\s*<dd>(.*?)</dd>', html)
        if section:
            return self.findallbyre('([^;<>,]*)', section.replace('and', ','), 'occupation')

    def findbirthdate(self, html):
        return self.findbyre('(?s)<dt>Date of birth</dt>\s*<dd>(.*?)</dd>', html)
    
    def finddeathdate(self, html):
        return self.findbyre('(?s)<dt>Date of death</dt>\s*<dd>(.*?)</dd>', html)

    def findmemberships(self, html):
        section = self.findbyre('(?s)<dt>Member of</dt>\s*<dd>(.*?)</dd>', html)
        if section:
            return self.findallbyre('(?s)>([^<>]*)<', section, 'organization')
        
    def findsiblings(self, html):
        section = self.findbyre('(?s)<dt>Sibling of</dt>\s*<dd>(.*?)</dd>', html)
        if section:
            return self.findallbyre('(?s)>([^<>]*)</a>', section, 'person')

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html, includesocial=False)


class NpgPersonAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P1816"
        self.dbid = None
        self.dbname = "National Portrait Gallery"
        self.urlbase = "https://www.npg.org.uk/collections/search/person/{id}"
        self.hrtre = "(<h1.*)<div class='view-results-options'>"
        self.language = 'en'

    def finddescription(self, html):
        return self.findbyre("<span class='largistText'>(.*?)<", html)

    def findnames(self, html):
        return [self.findbyre('<title>(.*?)[-<]', html)]

    def findinstanceof(self, html):
        return "Q5"

    def findoccupations(self, html):
        return self.findallbyre('/collections/search/group/\d+/([^\'"\s]*)', html, 'occupation')

    def findbirthdate(self, html):
        return self.findbyre("<span class='largistText'>[^<>]*\((\d+)-", html)

    def finddeathdate(self, html):
        return self.findbyre("<span class='largistText'>[^<>]*-(\d+)\)", html)

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html)


class GenealogicsAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P1819"
        self.dbid = "Q19847326"
        self.dbname = "genealogics.org"
        self.urlbase = 'http://www.genealogics.org/getperson.php?personID={id}&tree=LEO'
        self.hrtre = '(<ul class="nopad">.*?)<!-- end info -->'
        self.language = 'en'

    def prepare(self, html):
        return html.replace('&nbsp;', ' ').replace('&nbsp', ' ')

    def getvalue(self, field, html, dtype=None):
        return self.findbyre('(?s)"fieldname">\s*%s\s*</span></td>\s*<td[^<>]*>(?:<[^<>]*>)*(.+?)<'%field, html, dtype)

    def getallvalues(self, field, html, dtype=None):
        return self.findallbyre('(?s)"fieldname">\s*%s\s*</span></td>\s*<td[^<>]*>(?:<[^<>]*>)*(.+?)<'%field, html, dtype)

    def getfullvalue(self, field, html, dtype=None):
        return self.findbyre('(?s)"fieldname">\s*%s\s*</span></td>\s*<td[^<>]*>(.*?)</td>'%field, html, dtype)

    def getsecondvalue(self, field, html, dtype=None):
        section = self.findbyre('(?s)"fieldname">(\s*%s\s*</span>.*?)</tr>'%field, html)
        if section:
            return self.findbyre('<td.*?</td>\s*<td[^<>]*>(?:<[^<>]*>)*([^<>]*?)<', section, dtype)

    def findnames(self, html):
        return [
            self.findbyre('<title>([^<>]*):', html),
            self.findbyre('name="Keywords" content="(.*?)"', html),
            self.findbyre('name="Description" content="([^"]*):', html),
            self.findbyre('<h1[^<>]*>(.*?)<', html)
            ]

    def findlongtext(self, html):
        return self.findbyre('(?s)<ul class="nopad">(.*)<td class="databack">', html)

    def findinstanceof(self, html):
        return 'Q5'

    def findbirthdate(self, html):
        result = self.getvalue('Born', html)
        if result and "abt" not in result.lower():
            return result

    def findbirthplace(self, html):
        return self.getsecondvalue('Born', html, 'city')

    def findbaptismdate(self, html):
        return self.getvalue('Christened', html)

    def findgender(self, html):
        return self.getvalue('Gender', html, 'gender')

    def findnationality(self, html):
        return self.getvalue('Lived In', html, 'country')

    def findoccupations(self, html):
        return [self.getvalue('Occupation', html, 'occupation')]

    def finddeathdate(self, html):
        result = self.getvalue('Died', html)
        if result and "abt" not in result.lower():
            return result

    def finddeathplace(self, html):
        return self.getsecondvalue('Died', html, 'city')

    def findfather(self, html):
        return self.getvalue('Father', html, 'person')

    def findmother(self, html):
        return self.getvalue('Mother', html, 'person')

    def findchildren(self, html):
        sections = self.findallbyre('(?s)>Children[^<>]*<.*?(<table.*?</table>)', html)
        result = []
        for section in sections:
            result += self.findallbyre('>([^<>]*)</a>', section, 'person')
        return result

    def findsiblings(self, html):
        sections = self.findallbyre('(?s)>Siblings<.*?(<table.*?</table>)', html)
        result = []
        for section in sections:
            result += self.findallbyre('>([^<>]*)</a>', section, 'person')
        return result

    def findspouses(self, html):
        return self.getallvalues('Family(?: \d+)?', html, 'person')

    def findburialplace(self, html):
        return self.getsecondvalue('Buried', html, 'cemetary')

    def findsources(self, html):
        section = self.findbyre('(?s)(<span class="fieldname">Source.*?)</table>', html)
        if section:
            return self.findallbyre('~([^<>]*)\.', section, 'source')

class PssBuildingAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P1838"
        self.dbid = None
        self.dbname = "PSS-archi"
        self.urlbase = "http://www.pss-archi.eu/immeubles/{id}.html"
        self.hrtre = '<table class="idtable">(.*?)</table>'
        self.language = 'fr'

    def finddescription(self, html):
        return self.findbyre('(?s)<div id="infos">.*?<p>(.*?)</?p>', html)

    def findnames(self, html):
        return [self.findbyre('(?s)<h1 id="nom_immeuble">(.*?)<', html)]

    def findlongtext(self, html):
        return self.findbyre('(?s)<div id="infos">(.*?)</div>', html)

    def findinstanceof(self, html):
        return "Q41176"     

    def findcountry(self, html):
        return self.findbyre('<th>Pays</th>.*?>([^<>]+)</a>', html, 'country')

    def findadminloc(self, html):
        return self.findbyre('<th>Commune</th>.*?>([^<>]+)</a>', html, 'commune')

    def findaddress(self, html):
        result = self.findbyre('<th>Adresse[^<>]*?</th>.*?td>(.+?)</td>', html)
        if result:
            result = self.TAGRE.sub(" ", result)
            return result

    def findcoords(self, html):
        return self.findbyre('<th>Coordonn[^<>]+es</th>.*?>([^<>]+)</td>', html)

    def findinception(self, html):
        return self.findbyre('<th>Ann[^<>]*e</th>.*?td>(.*?)<', html)
    
    def findarchitects(self, html):
        archilist = self.findbyre('<th>Architecte\(s\).*?<ul(.*?)</ul>', html)
        if archilist:
            return self.findallbyre('<li>(?:<a[^<>]+>)?([^<>]+)</', archilist, 'architect')
    
    def findheights(self, html):
        return [self.findbyre('<th>Hauteur du toit</th>.*?span>([^<>]+)<', html)]


class CerlAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P1871'
        self.dbid = None
        self.dbname = 'CERL Thesaurus'
        self.urlbase = 'https://data.cerl.org/thesaurus/{id}'
        self.hrtre = '(<h3.*?)<h3>Other Formats'
        self.language = 'en'

    def getvalue(self, field, html, dtype=None):
        return self.findbyre('(?s)>%s</span><span[^<>]*>(?:<[^<>]*>)?([^<>]*)</'%field, html, dtype)

    def getvalues(self, field, html, dtype=None, link=False):
        section = self.findbyre('(?s)>%s</span>(.*?>)[^<>]+</span><span'%field, html) or\
                  self.findbyre('(?s)>%s</span>(.*)'%field, html)
        if section:
            return self.findallbyre('<%s[^<>]*>(.*?)[\(<]'%('a ' if link else 'span'), section, dtype)
        else:
            return []

    def findnames(self, html):
        return self.getvalues('Heading', html) + self.getvalues('Variant Name', html)

    def findlongtext(self, html):
        return '{}\n{}\n{}'.format(
            self.findbyre('(?s)<h3>General Note</h3>(.*?)<h3', html) or '',
            self.findbyre('(?s)<h3>More Information</h3>(.*?)<h3', html) or '',
            self.findbyre('(?s)<h3>Related Entries</h3>(.*?)<h3', html) or ''
            )

    def findbirthdate(self, html):
        section = self.getvalue('Biographical Data', html)
        if section:
            return self.findbyre('(.*) -', section)

    def finddeathdate(self, html):
        section = self.getvalue('Biographical Data', html)
        if section:
            return self.findbyre('- (.*)', section)

    def findbirthplace(self, html):
        values = self.getvalues('Place of Birth', html, 'city', link=True)
        if values:
            return values[0]
        else:
            return self.getvalue('Place of Birth', html, 'city')

    def finddeathplace(self, html):
        values = self.getvalues('Place of Death', html, 'city', link=True)
        if values:
            return values[0]
        else:
            return self.getvalue('Place of Death', html, 'city')

    def findoccupations(self, html):
        sections = self.getvalues('Profession / Occupation', html) +\
               self.getvalues('Activity', html) +\
               self.getvalues('Intellectual Responsibility', html)
        result = []
        for section in sections:
            self.findallbyre('([^;,]*)', section, 'occupation')
        return result

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html)

    def findnationality(self, html):
        return self.getvalue('Country', html, 'country')

    def findworkplaces(self, html):
        return self.getvalues('Place of Activity', html, 'city', link=True)

    def findchildren(self, html):
        return self.getvalues('Child', html, 'person', link=True)


class DiscogsAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P1953"
        self.dbid = "Q504063"
        self.dbname = "Discogs"
        self.urlbase = "https://www.discogs.com/artist/{id}"
        self.hrtre = '<div class="profile">(.*?)<div class="right">'
        self.language = 'en'
        self.escapeunicode = True

    def finddescriptions(self, html):
        return [
            self.findbyre('(?s)"description": "(.*?)"', html),
            self.findbyre('(?s)"description": "(.*?)\.', html)
            ]

    def findnames(self, html):
        result = [self.findbyre('<h1[^<>]*>(.*?)<', html)]
        section = self.findbyre('(?s)<div class="head">Variations:</div>(.*?)<!-- /content -->', html)
        if section:
            result += self.findallbyre('>([^<>]*)</a>', section)
        result.append(self.findbyre('(?s)<div class="head">Real Name:</div>.*?<div class="content">(.*?)</div>', html))
        section = self.findbyre('(?s)<div class="head">Aliases:</div>.*?<div class="content">(.*?)</div>', html)
        if section:
            result += self.findallbyre('>([^<>]*)</a>', section)
        return result

    def findlongtext(self, html):
        return self.findbyre('(?s)<div class="profile">(.*?)<!-- end profile -->', html)

    def findparts(self, html):
        section = self.findbyre('(?s)Members:</div>(.*?<a.*?)</div', html)
        if section:
            return self.findallbyre('>([^<>]+)</[sa]>', section, 'musician')

    def findmemberships(self, html):
        section = self.findbyre('(?s)In Groups:</div>(.*?<a.*?)</div', html)
        if section:
            return self.findallbyre('>([^<>]+)</[sa]>', section, 'group')

    def findoccupations(self, html):
        result = []
        section = self.findbyre('(?s)id="profile">(.*?)<', html)
        if section:
            parts = section.split(' and ')
            for part in parts[:5]:
                result += self.findallbyre('[\w\s\-]+', part, 'occupation', alt=['music-occupation'])
            return result

    def findinstruments(self, html):
        result = []
        section = self.findbyre('(?s)id="profile">(.*?)<', html)
        if section:
            parts = section.split(' and ')
            for part in parts[:5]:
                result += self.findallbyre('[\w\s\-]+', part, 'instrument')
            return result

    def findbirthdate(self, html):
        result = self.findbyre('born on (\d+\w{2} of \w+ \d{4})', html)
        if result:
            return self.findbyre('(\d+)', result) + self.findbyre('of( .*)', result)
        return self.findbyre('born on (\w+ \w+ \w+)', html) or\
               self.findbyre('Born\s*:?\s*(\d+ \w+ \d+)', html) or\
               self.findbyre('Born\s*:?\s*(\w+ \d+, \d+)', html)

    def findbirthplace(self, html):
        return self.findbyre('[bB]orn (?:on|:) .*? in ([\w\s]+)', html, 'city')

    def finddeathdate(self, html):
        return self.findbyre('died on (\w+ \w+ \w+)', html) or\
               self.findbyre('Died\s*:?\s*(\d+ \w+ \d+)', html) or\
               self.findbyre('Died\s*:?\s*(\w+ \d+, \d+)', html)

    def finddeathplace(self, html):
        return self.findbyre('[dD]ied (?:on|:) .*? in ([\w\s]+)', html, 'city')

    def findschools(self, html):
        return [self.findbyre('[eE]ducated at ([\w\s\']+)', html, 'university')]

    def findmixedrefs(self, html):
        section = self.findbyre('(?s)<div class="head">Sites:</div>\s*<div[^<>]*>(.*?)</div>', html) or\
                  self.findbyre('(?s)"sameAs": \[(.*?)\]', html)
        if section:
            return self.finddefaultmixedrefs(section)

    def findsiblings(self, html):
        section = self.findbyre('(?:[bB]rother|[sS]ister) of (<[^<>]*>(?:[^<>]|<[^<>]*>)*?)(?:\.|</div>)', html)
        if section:
            return self.findallbyre('>(.*?)<', section, 'person')


class ItalianPeopleAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P1986"
        self.dbid = "Q1128537"
        self.dbname = "Dizionario Biografico degli Italiani"
        self.urlbase = "http://www.treccani.it/enciclopedia/{id}_(Dizionario-Biografico)"
        self.hrtre = '<!-- module article full content -->(.*?)<!-- end module -->'
        self.language = 'it'

    def finddescription(self, html):
        return self.findbyre('<meta name="description" content="(.*?)"', html)

    def findnames(self, html):
        return [self.findbyre('(?s)<h1[^<>]*>(.*?)<', html)]

    def findlongtext(self, html):
        return self.findbyre('(?s)<!-- module article full content -->(.*?)<!-- end module -->', html)

    def findinstanceof(self, html):
        return "Q5"

    def findlastname(self, html):
        return self.findbyre('<strong>(.*?)<', html, 'lastname')

    def findfirstname(self, html):
        return self.findbyre('<span class="sc">(.*?)<', html, 'firstname') or\
               self.findbyre('<span class="sc">\s*(\w+)', html, 'firstname')

    def findbirthplace(self, html):
        return self.findbyre("[nN]acque (?:nell)?a (.*?)(?:,|\.| il| l'| l&#039;| nel)", html, 'city')

    def findbirthdate(self, html):
        return self.findbyre("[nN]acque.*? (?:il|l'|l&#039;)\s*(\d+ \w+\.? \d+)", html)

    def finddeathplace(self, html):
        return self.findbyre("[mM]or(?:ì|&igrave;) (?:nell)?a (.*?)(?:,|\.| il| l'| l&#039; |nel)", html, 'city')

    def finddeathdate(self, html):
        return self.findbyre("[mM]or(?:ì|&igrave;) .*? (?:il|l'|l&#039;)\s*(\d+ \w+\.? \d+)", html)


class DelargeAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P1988'
        self.dbid = 'Q20056651'
        self.dbname = 'Le Delarge'
        self.urlbase = 'https://www.ledelarge.fr/{id}'
        self.hrtre = '(<h1.*?)</div>'
        self.language = 'fr'
        self.escapehtml = True

    def findlongtext(self, html):
        result = self.findbyre('(?s)Présentation[^<>]*</span>\s*<span[^<>]*>(.*?)</span>', html)
        if result:
            result = [result]
        else:
            result = []
        result += self.findallbyre('<p align="justify">(.*?)</p>', html)
        return '\n'.join(result)
    
    def findinstanceof(self, html):
        return 'Q5'

    def findbirthdate(self, html):
        return self.findbyre('née? en (\d+)', html)

    def findbirthplace(self, html):
        return self.findbyre('née? [\w\s]+ à(.*?)[;<>]', html, 'city')

    def finddeathdate(self, html):
        return self.findbyre('([^<>;,]*), meurte? ', html)

    def finddeathplace(self, html):
        return self.findbyre('meurte? à (.*?)\.?[;<]', html, 'city')

    def findoccupations(self, html):
        section = self.findbyre('(?s)Technique\(s\)\s*:\s*</span>(.*?)<', html)
        if not section:
            section = self.findbyre('(?s)Type\(s\)\s*:\s*</span>(.*?)<', html)
        if section:
            return self.findallbyre('(\w+)', section, 'occupation')


class HalensisAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P2005"
        self.dbid = 'Q20680681'
        self.dbname = 'Catalogus Professorum Halensis'
        self.urlbase = 'http://www.catalogus-professorum-halensis.de/{id}.html'
        self.hrtre = '(<h1.*?)<!-- Ende -->'
        self.language = 'de'

    def findnames(self, html):
        result = self.findallbyre('<title>(.*?)<', html) +\
                 self.findallbyre('(?s)<h[12][^<>]*>(.*?)<', html)
        return [r.replace('\\n', ' ') for r in result]

    def findlongtext(self, html):
        return self.findbyre('(?s)<!-- custom html code -->(.*?)<!-- Ende -->', html)

    def findbirthdate(self, html):
        return self.findbyre('geboren:(?:<[^<>]*>)*([^<>]*\d{4})', html)

    def findbirthplace(self, html):
        return self.findbyre('gestorben:(?:<[^<>]*>)*[^<>]*\d{4}([^<>]*)', html, 'city')
        
    def finddeathdate(self, html):
        return self.findbyre('gestorben:(?:<[^<>]*>)*([^<>]*\d{4})', html)

    def finddeathplace(self, html):
        return self.findbyre('geboren:(?:<[^<>]*>)*[^<>]*\d{4}([^<>]*)', html, 'city')
        
    def findreligion(self, html):
        return self.findbyre('Konfession:(?:<[^<>]*>)*([^<>]+)', html, 'religion')

    def findemployers(self, html):
        return ['Q32120']            


class AcademiaeGroninganaeAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P2016"
        self.dbid = "Q20730803"
        self.dbname = "Catalogus Professorum Academiae Groninganae"
        self.urlbase = "https://hoogleraren.ub.rug.nl/hoogleraren/{id}"
        self.hrtre = '(<h1.*?)<!-- OVERIGE -->'
        self.language = 'nl'

    def getentry(self, naam, html, dtype=None):
        return self.findbyre('(?s){}<.*?>([^<>]*)</div>'.format(naam), html, dtype)

    def finddescription(self, html):
        return self.findbyre('<h1>(.*?)<', html)

    def findnames(self, html):
        return [self.findbyre('<h1>(.*?)[,<]', html)]

    def findinstanceof(self, html):
        return "Q5"

    def findlastname(self, html):
        return self.getentry('Achternaam', html, 'lastname')

    def findfirstname(self, html):
        return self.getdata('firstname', self.getentry('Voornamen en tussenvoegsel', html).split()[0].strip(','))

    def findgender(self, html):
        return self.getentry('Geslacht', html, 'gender')

    def findbirthdate(self, html):
        return self.getentry('Geboortedatum', html)

    def findbirthplace(self, html):
        return self.getentry('Geboorteplaats', html, 'city')

    def finddeathdate(self, html):
        return self.getentry('Overlijdensdatum', html)

    def finddeathplace(self, html):
        return self.getentry('Overlijdensplaats', html, 'city')

    def finddeathdate(self, html):
        return self.getentry('(?s)Overlijdensdatum<.*?>([^<>]*)</div>', html, 'gender')

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html)

    def findoccupations(self, html):
        return [self.getentry('Functie', html, 'occupation')]

    def findemployers(self, html):
        return ["Q850730"]

    def finddegrees(self, html):
        return [
            self.getentry('Graad', html, 'degree'),
            self.getentry('Titels', html, 'degree')
            ]

    def findschools(self, html):
        return [self.getentry('Universiteit promotie', html, 'university')]


class UlsterAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P2029"
        self.dbid = None
        self.dbname = "Dictionary of Ulster Biography ID"
        self.urlbase = "http://www.newulsterbiography.co.uk/index.php/home/viewPerson/{id}"
        self.hrtre = '(<h1.*?)<form'
        self.language = 'en'

    def finddescription(self, html):
        return self.findbyre('(?s)<div id="person_details">.*?</table>(.*?)<', html)

    def findnames(self, html):
        return [self.findbyre('<h1[^<>]*>(.*?)[<\(]', html)]

    def findlongtext(self, html):
        return self.findbyre('(?s)<div id="person_details">(.*?)</div>', html)

    def findinstanceof(self, html):
        return "Q5"

    def findbirthdate(self, html):
        return self.findbyre('(?s)<strong>\s*Born:.*?<td>(.*?)</td>', html)
    
    def finddeathdate(self, html):
        return self.findbyre('(?s)<strong>\s*Died:.*?<td>(.*?)</td>', html)

    def findoccupations(self, html):
        section = self.findbyre('(?s)<span class="person_heading_profession">(.*?)</span>', html)
        if section:
            section = section.split("and")
            result = []
            for sectionpart in section:
                result += self.findallbyre('([\w\s]+)', sectionpart, 'occupation')
            return result


class NgvAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P2041'
        self.dbid = None
        self.dbname = 'National Gallery of Victoria'
        self.urlbase = 'https://www.ngv.vic.gov.au/explore/collection/artist/{id}/'
        self.hrtre = '(<h1.*?)<h2'

    def findinstanceof(self, html):
        return 'Q5'

    def findnames(self, html):
        return self.findallbyre('rd-card__info">(.*?)<', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)<dt>Lived/worked</dt>\s*<dd>(.*?)</dd>', html)

    def findbirthdate(self, html):
        return self.findbyre('(?s)<dt>Born</dt>\s*<dd>((?:\d+ \w+ )?\d+)', html)

    def findbirthplace(self, html):
        return self.findbyre('(?s)<dt>Born</dt>\s*<dd>(?:\d+ \w+ )?\d+([^<>]*)', html, 'city')

    def finddeathdate(self, html):
        return self.findbyre('(?s)<dt>Died</dt>\s*<dd>((?:\d+ \w+ )?\d+)', html)

    def finddeathplace(self, html):
        return self.findbyre('(?s)<dt>Died</dt>\s*<dd>(?:\d+ \w+ )?\d+([^<>]*)', html, 'city')

    def findnationality(self, html):
        return self.findbyre('(?s)<dt>Nationality</dt>\s*<dd>(.*?)<', html, 'country')

    def findincollections(self, html):
        return [ 'Q1464509' ]


class JukeboxAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P2089'
        self.dbid = 'Q1362143'
        self.dbname = 'National Jukebox'
        self.urlbase = 'https://www.loc.gov/jukebox/artists/detail/id/{id}'
        self.urlbase = None # 503 forbidden
        self.hrtre = '<h1.*?</table>'
        self.language = 'en'

    def findnames(self, html):
        return [self.findbyre('(?s)<h1[^<>]*>(.*?)<', html)]

    def findinstanceof(self, html):
        return "Q5"

    def findoccupations(self, html):
        sections = self.findallbyre('(?s)<tr>(.*?)</tr>', html)
        result = []
        for section in sections:
            result += self.findbyre('(?s)<td>.*?<td>(.*?)<', section, 'occupation')
        return result

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html)


class FastAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P2163"
        self.dbid = "Q3294867"
        self.dbname = "FAST"
        self.urlbase = "https://experimental.worldcat.org/fast/{id}/"
        self.hrtre = '>Information about the Resource</h4>(.*?)<h4'
        self.language = 'en'
        self.escapehtml = True

    def findnames(self, html):
        result = []
        section = self.findbyre('(?s)"skos:prefLabel".*?<ul>(.*?)</ul>', html)
        if section:
            result += self.findallbyre('(?s)<li>(.*?)[\(<]', section)
        section = self.findbyre('(?s)"skos:altLabel".*?<ul>(.*?)</ul>', html)
        if section:
            result += self.findallbyre('(?s)<li>(.*?)[\(<]', section)
        result = [x.split('--')[-1] for x in result]
        return [", ".join(x.split(",")[:2]) if "," in x else x for x in result]

    def findinstanceof(self, html):
        return self.findbyre('(?s)Type:</a>.*?>([^<>]*)</a>', html, 'instanceof')

    def findfirstname(self, html):
        name = self.findbyre('(?s)SKOS Preferred Label:</a>.*?<li>(.*?)</li>', html)
        if name:
            return self.findbyre(',\s*(\w+)', name, 'firstname')
        
    def findlastname(self, html):
        name = self.findbyre('(?s)SKOS Preferred Label:</a>.*?<li>(.*?)</li>', html)
        if name:
            return self.findbyre('(.*?),', name, 'lastname')


class SvenskFilmAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P2168"
        self.dbid = "Q1139587"
        self.dbname = "Svensk Film Database"
        self.urlbase = 'http://www.svenskfilmdatabas.se/sv/item/?type=person&itemid={id}'
        self.hrtre = '(<table class="information-table">.*?)<h3>Relaterat</h3>'
        self.language = 'sv'

    def finddescriptions(self, html):
        description = self.findbyre('(?s)<h3>Beskrivning</h3>\s*<p>(.*?)<', html)
        if description:
            return [
                description,
                description.split(".")[0],
                ".".join(description.split(".")[:2]),
                ".".join(description.split(".")[:3]),
                ]

    def findnames(self, html):
        result = [self.findbyre('<h1[^<>]*>(.*?)<', html)]
        section = self.findbyre('(?s)<th>Alternativnamn</th>\s*<td>(.*?)</td>', html)
        if section:
            return result + self.findallbyre('>([^<>]+)<', section)
        else:
            return result

    def findlongtext(self, html):
        return self.findbyre('(?s)<h3>Beskrivning</h3>(.*?)</div>', html)

    def findinstanceof(self, html):
        return "Q5"

    def findoccupations(self, html):
        section = self.findbyre('(?s)<h3>Beskrivning</h3>\s*<p>\s*\w+\s*(.*?)[<\.]', html)
        if section:
            result = []
            parts = self.findallbyre('([\w\s]+)', section)
            for part in parts:
                result += [self.getdata('occupation', subpart) for subpart in part.split(' och ')]
            return ['Q2526255' if r == 'Q3455803' else r for r in result]

    def findnationality(self, html):
        return self.findbyre('(?s)<h3>Beskrivning</h3>\s*<p>\s*(\w+)', html, 'country')

    def findbirthdate(self, html):
        return self.findbyre('<time class="person__born" datetime="(.*?)"', html)


class NilfAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P2191'
        self.dbid = 'Q23023088'
        self.dbname = 'NILF'
        self.urlbase = 'https://www.fantascienza.com/catalogo/autori/{id}'
        self.hrtre = '<p class="bio">(.*?)<br class="clear"/>'
        self.language = 'it'

    def prepare(self, html):
        return html.replace('&nbsp;', ' ')

    def findnames(self, html):
        result = [self.TAGRE.sub('', self.findbyre('<h1>(.*?)</h1>', html))]
        section = self.findbyre('(?s)Noto anche como:(.*?)</p>', html)
        if section:
            result += self.findallbyre('(\w[\w\s]+)', self.TAGRE.sub('', section))
        return result

    def findlongtext(self, html):
        return self.findbyre('(?s)<p class="bio">(.*?)<div id="right">', html)

    def findnationality(self, html):
        return self.findbyre('Nazionalit.agrave.:<[^<>]*>(.*?)<', html, 'country')

    def findlanguagesspoken(self, html):
        return [self.findbyre('Lingua:<[^<>]*>(.*?)<', html, 'language')]

    def findlastname(self, html):
        return self.findbyre('<span class="cognome">(.*?)<', html, 'lastname')

    def findbirthdate(self, html):
        return self.findbyre('nato il</span>(.*?)<', html)

    def findawards(self, html):
        section = self.findbyre('(?s)Riconoscimenti:</span>(.*?)</p>', html)
        if section:
            return self.findallbyre('(\w[\w\s]+)', self.TAGRE.sub('', section), 'award')


class NgaAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P2252'
        self.dbid = None
        self.dbname = 'National Gallery of Art'
        self.urlbase = 'https://www.nga.gov/collection/artist-info.{id}.html'
        self.hrtre = '<div class="artist-intro detailheader">(.*?)</div>'
        self.language = 'en'

    def findnames(self, html):
        section = self.findbyre('(?s)<dd class="description">(.*?)</dd>', html)
        if section:
            return [self.findbyre('<dt class="artist">(.*?)<', html)] + self.findallbyre('(\w.+)', section)
        else:
            return [self.findbyre('<dt class="artist">(.*?)<', html)]

    def findnationality(self, html):
        return self.findbyre('(?s)<dd class="lifespan">([^<>]+?),', html, 'country')

    def findbirthdate(self, html):
        return self.findbyre('(?s)<dd class="lifespan">[^<>]+,([^<>]+)-', html)

    def finddeathdate(self, html):
        return self.findbyre('(?s)<dd class="lifespan">[^<>]+-([^<>\-]+)', html)

    def findincollections(self, html):
        return ['Q214867']


class OrsayAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P2268"
        self.dbid = None
        self.dbname = "Musee d'Orsay"
        self.urlbase = "http://www.musee-orsay.fr/fr/espace-professionnels/professionnels/chercheurs/rech-rec-art-home/notice-artiste.html?nnumid={id}"
        self.hrtre = '(<h2.*?)<div class="unTiers.notice">'
        self.language = 'fr'

    def finddescription(self, html):
        return self.findbyre('(?s)<h6>Documentation</h6>(.*?)</div>', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)<h6>Commentaire</h6>(.*?)<(?:h\d|div)', html)

    def findnames(self, html):
        section = self.findbyre('(?s)(<h2>.*?)</div>', html)
        if section:
            result = self.findallbyre('>(.*?)<', section)
            return [r for r in result if ':' not in r]

    def findisinstanceof(self, html):
        return "Q5"

    def findgender(self, html):
        return self.findbyre('Sexe\s*:\s*(.*?)<', html, 'gender')

    def findbirthdate(self, html):
        return self.findbyre('Naissance</h6>([^<>,]*?\d{4}[^<>,]*?)[,<]', html)

    def findbirthplace(self, html):
        return self.findbyre('Naissance</h6>[^,<>]*?,([^<>]*)', html, 'city')

    def finddeathdate(self, html):
        return self.findbyre('D.c.s</h6>([^<>,]*?\d{4}[^<>,]*?)[,<]', html)

    def finddeathplace(self, html):
        return self.findbyre('D.c.s</h6>[^,<>]*?,([^<>]*)', html, 'city')

    def findnationality(self, html):
        return self.findbyre('Nationalit. pr.sum.e</h6>(.*?)<', html, 'country')

    def findoccupations(self, html):
        section = self.findbyre('(?s)Documentation(</h6>.*?<)[/h]', html)
        return self.findallbyre('(?s)>(.*?)<', section, 'occupation')


class ArtHistoriansAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P2332"
        self.dbid = "Q17166797"
        self.dbname = "Dictionary of Art Historians"
        self.urlbase = "http://arthistorians.info/{id}"
        self.hrtre = '(<h1.*?>)Citation</h2>'
        self.language = 'en'

    def finddescription(self, html):
        return self.findbyre('name="(?s)dcterms.description" content="(.*?)"', html)

    def findnames(self, html):
        section = (self.findbyre('(?s)">Full Name:(.*?clearfix">)', html) or "") +\
                  (self.findbyre('(?s)">Other Names:(.*?clearfix">)', html) or "")
        return self.findallbyre('"field-item .*?">(.*?)<', section)

    def findlongtext(self, html):
        return self.findbyre('(?s)<div class="field-label">Overview:(.*?)<div class="field-label">', html)

    def findinstanceof(self, html):
        return "Q5"

    def findfirstname(self, html):
        return self.findbyre('dcterms.title" content="[^<>"]+,\s*(\w+)', html, 'firstname')

    def findlastname(self, html):
        return self.findbyre('dcterms.title" content="([^<>"]+),', html, 'lastname')

    def findbirthdate(self, html):
        return self.findbyre('Date Born:.*?>([^<>]+)</span>', html)

    def findnationality(self, html):
        return self.findbyre('Home Country:.*?>([^<>]+)</', html, 'country')


class CesarAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P2340"
        self.dbid = None
        self.dbname = "César"
        self.urlbase = "http://cesar.org.uk/cesar2/people/people.php?fct=edit&person_UOID={id}"
        self.hrtre = '</H1>(.*?)<H2>'
        self.language = 'en'

    def getvalue(self, field, html, dtype = None):
        return self.findbyre("(?s)<TR><TD[^<>]*keyColumn[^<>]*>[^<>]*%s[^<>]*</TD>[^<>]*<TD[^<>]*valueColumn[^<>]*>(.*?)<"%field, html.replace("&nbsp;", " "), dtype)

    def findnames(self, html):
        return [
            self.findbyre("'objectSummary'>(.*?)</B>", html),
            self.findbyre("'objectSummary'>(.*?)</I>", html),
            self.getvalue("Pseudonym", html)
            ]

    def findfirstname(self, html):
        return self.getvalue("First name", html, "firstname")

    def findlastname(self, html):
        return self.getvalue("Last name", html, "lastname")

    def findbirthdate(self, html):
        return self.getvalue("Birth date", html)

    def finddeathdate(self, html):
        return self.getvalue("Death date", html)

    def findgender(self, html):
        return self.getvalue("Gender", html, "gender")

    def findnationality(self, html):
        return self.getvalue("Nationality", html, "country")

    def findoccupations(self, html):
        section = self.getvalue("Skills", html)
        if section:
            return self.findallbyre('(\w+)', section, 'occupation')
            


class AgorhaAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P2342"
        self.dbid = "Q21994367"
        self.dbname = "AGORHA"
        self.urlbase = "http://agorha.inha.fr/inhaprod/ark:/54721/002{id}"
        self.hrtre = '(<h2.*?)<!-- Vue de la notice -->'
        self.language = 'fr'

    def finddescription(self, html):
        return self.findbyre('name="dcterms.description" content="(.*?)"', html)

    def findnames(self, html):
        return [self.findbyre('(?s)<h2[^<>]*>(.*?)[\(<]', html)]

    def findgender(self, html):
        return self.findbyre('(?s)>Sexe</th>.*?<td>(.*?)</', html, 'gender')

    def findnationality(self, html):
        return self.findbyre('(?s)>Nationalit.</th>.*?<td>(.*?)</', html, 'country')

    def findbirthdate(self, html):
        result = self.findbyre('(?s)>Naissance</th>.*?<td>(.*?)<', html)
        if result and "/" not in result:
            return result
    
    def finddeathdate(self, html):
        result = self.findbyre('(?s)>D.c.s</th>.*?<td>(.*?)<', html)
        if result and "/" not in result:
            return result


class OdisAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P2372'
        self.dbid = 'Q3956431'
        self.dbname = 'ODIS'
        if self.id.startswith('PS'):
            self.id = self.id[3:]
            self.urlbase = 'http://www.odis.be/lnk/PS_{id}'
            self.urlbase3 = 'https://www.odis.be/hercules/CRUDscripts/pers/identificatie/getPublicdata.script.php?persid={id}&websiteOutputIP=www.odis.be&taalcode=nl'
            self.skipfirst = True
        else:
            self.urlbase = None
        self.hrtre = '<h2>Identificatie</h2>(.*?)<h2>Varia</h2>'
        self.language = 'nl'

    def findinstanceof(self, html):
        return 'Q5'

    def findnames(self, html):
        return self.findallbyre('<OMSCHRIJVING>(.*?)<', html)

    def finddescription(self, html):
        return self.findbyre('(?s)<b>Biografische schets</b>\s*</td>\s*</tr>\s*<tr>\s*<td>\s*<[pP]>([^<>\.]*)', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)<b>Biografische schets</b>\s*</td>\s*</tr>\s*<tr>\s*<td>\s*<[pP]>(.*?)</td>', html)

    def findlastname(self, html):
        return self.findbyre('(?s)<td[^<>]*>familienaam</td>\s*<td[^<>]*>(.*?)<', html, 'lastname')

    def findfirstname(self, html):
        return self.findbyre('(?s)<td[^<>]*>roepnaam</td>\s*<td[^<>]*>(.*?)<', html, 'firstname') or\
               self.findbyre('(?s)<td[^<>]*>eerste voornaam</td>\s*<td[^<>]*>(.*?)<', html, 'firstname')

    def findpseudonyms(self, html):
        return self.findallbyre('(?s)<td[^<>]*>[^<>]*pseudoniem[^<>]*</td>\s*<td[^<>]*>(.*?)<', html)

    def findresidences(self, html):
        section = self.findbyre('(?s)<b>Woon- en verblijfplaatsen</b>\s*</td>\s*</tr>\s*<tr>(.*?)</tbody>', html)
        if section:
            result = []
            subsections = self.findallbyre('(?s)(<tr.*?</tr>)', section)
            for subsection in subsections:
                result.append(
                    self.findbyre('<td width="auto">([^<>]*)</td>', subsection, 'city') or\
                    self.findbyre('<span[^<>]*>(.*?)<', subsection, 'city')
                    )
            return result

    def findoccupations(self, html):
        section = self.findbyre('(?s)<b>Professionele loopbaan</b>\s*</td>\s*</tr>\s*<tr>(.*?)</tbody>', html)
        if section:
            return self.findallbyre('(?s)<tr[^<>]*>\s*<td[^<>]*>(.*?)</td>', section, 'occupation')

    def findmemberships(self, html):
        section = self.findbyre('(?s)<b>Engagementen in organisaties en instellingen</b>\s*</td>\s*</tr>\s*<tr>(.*?)</tbody>', html)
        if section:
            return self.findallbyre('(?s)<tr[^<>]*>\s*<td[^<>]*>[^<>]*</td>\s*<td[^<>]*>([^<>]*)</td>', section, 'organization') +\
                   self.findallbyre('<a[^<>]*>(.*?)<', section, 'organization')
        
    def findpositions(self, html):
        section = self.findbyre('(?s)<b>Politieke mandaten</b>\s*</td>\s*</tr>\s*<tr>(.*?)</tbody>', html)
        if section:
            result = []
            for subsection in self.findallbyre('(?s)<tr[^<>]*>(.*?)</tr>', section):
                parts = self.findallbyre('<span[^<>]*>(.*?)<', subsection)
                result += self.findbyre('(.*)', ' '.join(parts), 'position')
            return result

    def findlanguagesspoken(self, html):
        section = self.findbyre('(?s)<b>Talen</b>\s*</td>\s*</tr>\s*<tr>(.*?)</tbody>', html)
        if section:
            return self.findallbyre('(?s)<tr[^<>]*>\s*<td[^<>]*>(.*?)[<\(]', section, 'language')

    def findwebpages(self, html):
        section = self.findbyre('(?s)<b>Online bijlagen</b>\s*</td>\s*</tr>\s*<tr>(.*?)</tbody>', html)
        if section:
            result = self.findallbyre('<a href="(.*?)[#"', section)
            return [r for r in result if not 'viaf' in r]
            
    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html)


class AcademicTreeAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P2381'
        self.dbid = 'Q21585670'
        self.dbname = 'Academic Family Tree'
        self.urlbase = 'https://academictree.org/chemistry/peopleinfo.php?pid={id}'
        self.hrtre = '(<h1.*?)<div class="rightcol'
        self.language = 'en'

    def findinstanceof(self, html):
        return 'Q5'

    def findnames(self, html):
        return [self.findbyre('(?s)<h1[^<>]*>(.*?)<', html)]

    def findlongtext(self, html):
        return self.findbyre('(?s)</h1>(\s*<table.*?)<table', html)

    def finddescription(self, html):
        return self.findbyre('(?s)Commentaire biographique</th>.*?<td>(.*?)</td>', html)

    def findemployers(self, html):
        section = self.findbyre('(?s)Affiliations:.*?(<.*?</table>)', html)
        if section:
            return self.findallbyre('>([^<>]*)</a>', section, 'university', alt=['employer'])
        
    def findadvisors(self, html):
        section = self.findbyre('(?s)Parents</h4>(.*?)<h\d', html)
        if section:
            return self.findallbyre('(?s)>([^<>]*)</a>', section.replace('&nbsp;', ' '), 'scientist', skips = [ 'university', 'employer' ])

    def finddocstudents(self, html):
        section = self.findbyre('(?s)Children</h4>(.*?)<h\d', html)
        if section:
            return self.findallbyre('(?s)>([^<>]*)</a>', section.replace('&nbsp;', ' '), 'scientist', skips = [ 'university', 'employer' ])

    def findbirthdate(self, html):
        return self.findbyre('Bio:(?:<[^<>]*>)*\(([^<>]*) -', html)

    def finddeathdate(self, html):
        return self.findbyre('Bio:(?:<[^<>]*>)*\([^<>]* - ([^<>]*?)\)', html)

    def findwebsite(self, html):
        return self.findbyre('(?s)>Site web</th>.*?>([^<>]*)</a>', html)

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html)

    def findworkfields(self, html):
        section = self.findbyre('(?s)Area:</[^<>]*>([^<>]*)<', html)
        if section:
            return self.findallbyre("([\w\s']+)", section, 'subject')


class CthsAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P2383'
        self.dbid = None
        self.dbname = 'Comité des travaux historiques et scientifiques'
        self.urlbase = 'http://cths.fr/an/savant.php?id={id}'
        self.hrtre = '<div class=\s*title>(.*?</div id =biographie>)'
        self.language = 'fr'

    def findnames(self, html):
        return [self.findbyre('<title>[^<>]*?-(.*?)<', html),
                self.findbyre('id=proso_bio_detail>([^<>]*) est un', html)
                ]

    def findfirstname(self, html):
        return self.findbyre('<h2>.*?<strong>(.*?)<', html, 'firstname')

    def findlastname(self, html):
        return self.findbyre('<h2>(.*?)<', html, 'lastname')
    
    def finddescription(self, html):
        return self.findbyre('proso_bio_detail>(.*?)<', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)<div id =biographie>(.*?)</fieldset>', html)

    def findbirthdate(self, html):
        return self.findbyre('Naissance: ((?:\d+ )?(?:\w+ )?\d{4})', html)

    def findbirthplace(self, html):
        return self.findbyre('Naissance: [^<>\-]* à ([^<>\(]*)', html, 'city')

    def finddeathdate(self, html):
        return self.findbyre('Décès: ((?:\d+ )?(?:\w+ )?\d{4})', html)

    def finddeathplace(self, html):
        return self.findbyre('Décès: [^<>\-]* à ([^<>\(]*)', html, 'city')

    def findmemberships(self, html):
        section = self.findbyre('(?s)<fieldset id="fieldset_societes">(.*?)</fieldset>', html)
        if section:
            return self.findallbyre('>([^<>]+)</A>', html, 'organization')

    def findoccupations(self, html):
        result = []
        section = self.findbyre('id=proso_bio_detail>[^<>]* est une? ([^<>]*)', html)
        if section:
            subsections = section.split(' et ')
            for subsection in subsections:
                result += [self.getdata('occupation', part) for part in subsection.split(',')]
            return result


class TransfermarktAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P2446'
        self.dbid = 'Q2449070'
        self.dbname = 'Transfermarkt'
        self.urlbase = 'https://www.transfermarkt.com/-/profil/spieler/{id}'
        self.hrtre = '<span>Player data</span>(.*?)<div class="box'
        self.language = 'en'

    def findnames(self, html):
        return [
            self.findbyre('"keywords" content="([^"]+),', html),
            self.findbyre('<title>([^<>]*) - ', html),
            self.findbyre('(?s)Full Name:.*?<td>(.*?)<', html),
            ]

    def findlongtext(self, html):
        return self.findbyre('(?s)>Further information</span>(.*?)<div class="box', html)

    def findlastname(self, html):
        return self.findbyre('<h1 itemprop="name">[^<>]*<b>(.*?)<', html, 'lastname')

    def findfirstname(self, html):
        return self.findbyre('<h1 itemprop="name">([^<>]*)<b>', html, 'firstname')

    def findinstanceof(self, html):
        return 'Q5'

    def findoccupations(self, html):
        return ['Q937857']

    def findbirthdate(self, html):
        return self.findbyre('(?s)<span itemprop="birthDate" class="dataValue">(.*?)[\(<]', html)
    
    def finddeathdate(self, html):
        return self.findbyre('(?s)<span itemprop="deathDate" class="dataValue">(.*?)[\(<]', html)

    def findbirthplace(self, html):
        return self.findbyre('(?s)<span itemprop="birthPlace">(.*?)<', html)
    
    def finddeathplace(self, html):
        return self.findbyre('(?s)<span itemprop="deathPlace">(.*?)<', html)
    
    def findnationalities(self, html):
        return self.findallbyre('(?s)<span itemprop="nationality">(.*?)<', html)    
        
    def findheight(self, html):
        return self.findbyre('(?s)<span itemprop="height" class="dataValue">(.*?)<', html)
    
    def findteampositions(self, html):
        result = []
        for section in [
            self.findbyre('(?s)<span>Main position\s*:</span(>.*?<)/div>', html),
            self.findbyre('(?s)<span>Other position\(s\)\s*:</span(>.*?<)/div>', html)
            ]:
            if section:
                result += self.findallbyre('>([^<>]*)<', section, 'footballposition')
        return result

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html)

    def findwebsite(self, html):
        return self.findbyre('(?s)<a href="([^"]*)"[^<>]*>\s*<img src="https://tmsi.akamaized.net/icons/.svg"', html)

    def findsportteams(self, html):
        section = self.findbyre('<div class="box transferhistorie">(.*?)<div class="box', html)
        if section:
            return self.findallbyre('(?s)<td class="hauptlink no-border-links hide-for-small vereinsname">\s*<[^<>]*>(.*?)<', html, 'footballteam')


class KnawAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P2454"
        self.dbid = "Q21491701"
        self.dbname = "KNAW"
        self.urlbase = "http://www.dwc.knaw.nl/biografie/pmknaw/?pagetype=authorDetail&aId={id}"
        self.hrtre = '(<h1.*?)<div class="sidebar">'
        self.language = 'en'

    def finddescription(self, html):
        return self.findbyre('<h1>(.*?)</h1>', html)

    def findnames(self, html):
        return [self.findbyre('<h1>(.*?)[\(<]', html)]

    def findinstanceof(self, html):
        return "Q5"

    def findgender(self, html):
        return self.findbyre('<strong>Gender</strong>:?(.*?)<', html, 'gender')

    def findbirthplace(self, html):
        return self.findbyre('Born:([^<>]*),', html, 'city')

    def findbirthdate(self, html):
        return self.findbyre('Born:[^<>]*,([^<>]*)', html)
    
    def finddeathplace(self, html):
        return self.findbyre('Died:([^<>]*),', html, 'city')

    def finddeathdate(self, html):
        return self.findbyre('Died:[^<>]*,([^<>]*)', html)

    def findmemberships(self, html):
        section = self.findbyre('(?s)Memberships(?:<[^<>]*>)?\s*:(.*?)</div>', html)
        if section:
            return self.findallbyre('<em>(.*?)<', section, 'organization')


class DblpAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P2456'
        self.dbid = 'Q1224715'
        self.dbname = 'DBLP'
        self.urlbase = 'https://dblp.org/pid/{id}'
        self.hrtre = '<h3>Person information</h3>(.*?)<h3>'
        self.language = 'en'

    def findlongtext(self, html):
        return self.findbyre('(?s)<h3>Person information</h3>(.*?)<h3>', html)

    def findnames(self, html):
        return self.findallbyre('class="this-person" itemprop="name">(.*?)<', html)
               
    def findemployers(self, html):
        return self.findallbyre('(?s)>affiliation[^<>]*</em>.*?>([^<>]*)</span>', html, 'university')

    def findawards(self, html):
        return self.findallbyre('(?s)>award:</em>.*?>([^<>]*)</span>', html, 'award')

    def findbirthdate(self, html):
        return self.findallbyre('<li>\s*(\d+)\s*-\s*\d+\s*<', html)
        
    def finddeathdate(self, html):
        return self.findallbyre('<li>\s*\d+\s*-\s*(\d+)\s*<', html)


class TheatricaliaAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P2469'
        self.dbid = 'Q24056151'
        self.dbname = 'Theatricalia'
        self.urlbase = 'http://theatricalia.com/person/{id}'
        self.hrtre = '(<h1.*?<h2 class="sm">Tools</h2>)'
        self.language = 'en'

    def findlongtext(self, html):
        return self.findbyre('(?s)<div itemprop="description">(.*?)</div', html)

    def findinstanceof(self, html):
        return self.findbyre('itemtype="http://schema.org/(.*?)"', html, 'instanceof')

    def findnames(self, html):
        return self.findallbyre('itemprop="name">(.*?)<', html)

    def findbirthdate(self, html):
        result = self.findbyre('itemprop="birthDate" datetime="(.*?)"', html)
        if result:
            return result.replace('-00', '')
    
    def finddeathdate(self, html):
        result = self.findbyre('itemprop="birthDate" datetime="(.*?)"', html)
        if result:
            return result.replace('-00', '')

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html, includesocial=False)

    def findoccupations(self, html):
        result = []
        if self.findbyre('(?s)itemprop="performerIn"[^<>]*>(\s*)<', html):
            result.append('Q2259451')
        result += self.findallbyre('(?s)itemprop="performerIn"[^<>]*>(.*?)<', html, 'theater-occupation', alt=['occupation'])
        return result


class KinopoiskAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P2604'
        self.dbid = 'Q2389071'
        self.dbname = 'KinoPoisk'
        self.urlbase = 'https://www.kinopoisk.ru/name/{id}/'
        self.hrtre = '(<h1.*?</table>)'
        self.language = 'ru'

    def findnames(self, html):
        return [self.findbyre('<h1[^<>]*>(.*?)<', html)] +\
               self.findallbyre('"alternateName">(.*?)<', html) +\
               self.findallbyre('title" content="(.*?)[\(<]', html)

    def findinstanceof(self, html):
        return "Q5"

    def findoccupations(self, html):
        return self.findallbyre('"jobTitle" content="(.*?)"', html, 'film-occupation', alt=['occupation'])

    def findbirthdate(self, html):
        return self.findbyre('"birthDate" content="(.*?)"', html) or\
               self.findbyre('birthDate="(.*?)"', html)
    
    def findheight(self, html):
        return self.findbyre('(?s)>рост</td>.*?>([^<>]*?)</span>', html)

    def findbirthplace(self, html):
        return self.findbyre('(?s)class="birth"[^<>]*>\s*<span><a[^<>]*>([^<>]*)</a>', html, 'city')


class CsfdAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P2605'
        self.dbid = 'Q3561957'
        self.dbname = 'ČSFD'
        self.urlbase = 'https://www.csfd.cz/tvurce/{id}'
        #self.urlbase = None
        self.language = 'cs'
        self.hrtre = '(<div class="info">.*?</div>)'

    def findnames(self, html):
        f = codecs.open('result.html', 'w', 'utf-8')
        f.write(html)
        f.close()
        return [self.findbyre('<h1.*?>(.*?)<', html)]

    def findlongtext(self, html):
        return self.findbyre('(?s)>\s*Biografie\s*<.*?<div class="content">(.*?)</div>', html)

    def findbirthdate(self, html):
        return self.findbyre('\snar\.(.*)', html)

    def findbirthplace(self, html):
        return self.findbyre('(?s)</h1>.*?<br>(.*?)<.*<div class="navigation">', html, 'city')

    def findoccupations(self, html):
        return self.findallbyre('>([^<>]*) filmografie<', html, 'film-occupation', alt=['occupation'])

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html, includesocial=False)


class FilmportalAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P2639'
        self.dbid = "Q15706812"
        self.dbname = "Filmportal"
        self.urlbase = "http://www.filmportal.de/film/{id}"
        self.urlbase2 = "http://www.filmportal.de/person/{id}"
        self.hrtre = '<h1>(.*?)<div class="panel-panel sidebar">'
        self.language = 'de'

    def finddescription(self, html):
        return self.findbyre('(?s)<div class="intertitle">(.*?)</div>', html)

    def findnames(self, html):
        result = [
            self.findbyre('Originaltitel \(\w+\)(.*?)<', html),
            self.findbyre('<meta name="title" content="(.*?)[\|<]', html),
            self.findbyre('(?s)<h1>(.*?)<', html),
            ]
        section = self.findbyre('(?s)Weitere Namen</div>(.*?)</div>', html)
        if section:
            result += self.findallbyre('(?s)>(.*?)[\(<]', section)
        return result

    def findlongtext(self, html):
        return self.findbyre('(?s)<h2[^<>*]>(?:Inhalt|Biografie)</h2>(.*?)<(?:div|section)\s*class=', html)

    def findinstanceof(self, html):
        if "/film/" in self.url:
            return "Q11424"
        elif "/person/" in self.url:
            return "Q5"

    def findorigcountry(self, html):
        return self.findbyre('(?s)<span\s*class="movie-region-names"\s*>.*?<span\s*>(.*?)<', html, 'country')

    def findpubdate(self, html):
        return self.findbyre('(?s)<span\s*class="movie-year"\s*>\s*(\d+)', html)

    def findmoviedirectors(self, html):
        section = self.findbyre('(?s)<h3>Regie</h3>.*?(<ul.*?</ul>)', html)
        if section:
            return self.findallbyre('>([^<>]*)</a>', section, 'filmmaker')
    
    def findscreenwriters(self, html):
        section = self.findbyre('(?s)<h3>Drehbuch</h3>.*?(<ul.*?</ul>)', html)
        if section:
            return self.findallbyre('>([^<>]*)</a>', section, 'filmmaker')

    def finddirectorsphotography(self, html):
        section = self.findbyre('(?s)<h3>Kamera</h3>.*?(<ul.*?</ul>)', html)
        if section:
            return self.findallbyre('>([^<>]*)</a>', section, 'filmmaker')

    def findmovieeditors(self, html):
        section = self.findbyre('(?s)<h3>Schnitt</h3>.*?(<ul.*?</ul>)', html)
        if section:
            return self.findallbyre('>([^<>]*)</a>', section, 'filmmaker')

    def findcomposers(self, html):
        section = self.findbyre('(?s)<h3>Musik</h3>.*?(<ul.*?</ul>)', html)
        if section:
            return self.findallbyre('>([^<>]*)</a>', section, 'composer')

    def findcast(self, html):
        section = self.findbyre('(?s)<h3>Darsteller</h3>.*?(<ul.*?</ul>)', html)
        if section:
            return self.findallbyre('>([^<>]*)</a>', section, 'actor')
        
    def findprodcoms(self, html):
        section = self.findbyre('(?s)<h3>Produktionsfirma</h3>.*?(<ul.*?</ul>)', html)
        if section:
            return self.findallbyre('>([^<>]*)</a>', section, 'filmcompany')

    def findproducers(self, html):
        section = self.findbyre('(?s)<h3>Produzent</h3>.*?(<ul.*?</ul>)', html)
        if section:
            return self.findallbyre('>([^<>]*)</a>', section, 'filmmaker')

    def finddurations(self, html):
        return self.findallbyre('>Länge:.*?<div[^<>]*>[^<>]*?(\d+ min)[^<>]*<', html)

    def findoccupations(self, html):
        section = self.findbyre('<div class="[^"]*occupation field[^"]*">(.*?)<', html)
        if section:
            return self.findallbyre('([\w\s]+)', section, 'occupation')

    def findbirthplace(self, html):
        return self.findbyre('(?s)"field-birth-city">(.*?)<', html, 'city')

    def finddeathplace(self, html):
        return self.findbyre('(?s)"field-death-city">(.*?)<', html, 'city')

    def findbirthdate(self, html):
        return self.findbyre('(?s)"field-birth-date">.*?"datetime">(.*?)<', html)

    def finddeathdate(self, html):
        return self.findbyre('(?s)"field-death-date">.*?"datetime">(.*?)<', html)


class CageMatchAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P2728'
        self.dbid = 'Q64902023'
        self.dbname = 'CageMatch'
        self.urlbase = 'https://www.cagematch.net//?id=2&nr={id}'
        self.hrtre = '<div class="LayoutContent">(.*?)<div class="LayoutRightPanel">'
        self.language = 'de'

    def getvalue(self, field, html, dtype=None):
        return self.findbyre('(?s)<div class="InformationBoxTitle">%s:</div>\s*<div class="InformationBoxContents">(.*?)</div>'%field, html, dtype)

    def getvalues(self, field, html, dtype=None):
        section = self.getvalue(field, html)
        if section:
            return self.findallbyre('>([^<>]*)<', '>' + section + '<', dtype)

    def findlanguagenames(self, html):
        result = []
        section = self.findbyre('Also known as(.*?)<', html)
        if section:
            result += section.split(',')
        result += self.getvalues('Alter egos', html)
        section = self.getvalue('Nicknames', html)
        if section:
            result += self.findallbyre('"([^,]+)"', section)
        return [('en', res) for res in result] + [('de', res) for res in result]

    def findlongtext(self, html):
        return self.findbyre('(?s)<div id="hiddenText1"[^<>]*>(.*?)</div>', html)

    def findbirthplace(self, html):
        return self.getvalue('Birthplace', html, 'city')

    def findgender(self, html):
        return self.getvalue('Gender', html, 'gender')

    def findheight(self, html):
        section = self.getvalue('Height', html)
        if section:
            return self.findbyre('\((.*?)\)', section)

    def findweights(self, html):
        section = self.getvalue('Weight', html)
        if section:
            return [
                self.findbyre('(\d+ lbs)', section),
                self.findbyre('(\d+ kg)', section)
                ]
        
    def findsports(self, html):
        return self.getvalues('Background in sports', html)

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(self.getvalue('WWW', html) or '')

    def findoccupations(self, html):
        preoccs = self.getvalues('Roles', html)
        return [self.findbyre('([^\(\)]+)', preocc or '', 'occupation') for preocc in preoccs] +\
               self.getvalues('Active Roles', html, 'occupation')


class PerseeAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P2732'
        self.dbid = 'Q252430'
        self.dbname = 'Persée'
        self.urlbase = 'https://www.persee.fr/authority/{id}'
        self.hrtre = '(<h2 itemprop="name">.*?)</div>'
        self.language = 'fr'

    def findinstanceof(self, html):
        return 'Q5'

    def findlongtext(self, html):
        return self.findbyre('<p itemprop="description">(.*?)</p>', html)

    def findnames(self, html):
        return [self.findbyre('<h2 itemprop="name">(.*?)[<\(]', html)]

    def findbirthdate(self, html):
        section = self.findbyre('<h2 itemprop="name">(.*?)</h2>', html)
        if section:
            return self.findbyre('\(([\s\w]+)-', section)
        
    def finddeathdate(self, html):
        section = self.findbyre('<h2 itemprop="name">(.*?)</h2>', html)
        if section:
            return self.findbyre('-([\w\s]+)\)', section)

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html, includesocial = False)
    

class PhotographersAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P2750'
        self.dbid = 'Q23892012'
        self.dbname = "Photographers' Identity Catalog"
        self.urlbase = 'https://pic.nypl.org/constituents/{id}'
        self.hrtre = '(<div class="bio">.*</section>)'
        self.language = 'en'

    def findgender(self, html):
        return self.findbyre('<span class="gender">(.*?)<', html, 'gender')

    def findnames(self, html):
        return [ self.findbyre('<h1[^<>]*>(.*?)<', html) ]

    def findoccupations(self, html):
        return self.findallbyre('role\.TermID=\d*">(.*?)<', html, 'occupation')

    def findnationality(self, html):
        return self.findbyre('<h2 class="subtitle">(.*?)[<,]', html, 'country')

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html)

    def findbirthdate(self, html):
        return self.findbyre('(?s)Birth\s*\((.*?)\)', html)

    def finddeathdate(self, html):
        return self.findbyre('(?s)Death\s*\((.*?)\)', html)

    def findbirthplace(self, html):
        return self.findbyre('(?s)Birth[^<>]*</h4>\s*<p>(.*?)<', html.replace('<br />', ' '), 'city')

    def finddeathplace(self, html):
        return self.findbyre('(?s)Death[^<>]*</h4>\s*<p>(.*?)<', html.replace('<br />', ' '), 'city')

    def findworkplaces(self, html):
        return self.findallbyre('(?s)Active in[^<>]*</h4>\s*<p>(.*?)<', html.replace('<br />', ' '), 'city') +\
               self.findallbyre('(?s)Studio or Business[^<>]*</h4>\s*<p>(.*?)<', html.replace('<br />', ' '), 'city')

    def findincollections(self, html):
        section = self.findbyre('(?s)<h3>Found in collections</h3>.*?<ul.*?>(.*?)</ul>', html)
        if section:
            return self.findallbyre('<a[^<>]*>(.*?)<', section, 'museum')


class CanadianBiographyAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P2753'
        self.dbid = 'Q838302'
        self.dbname = 'Dictionary of Canadian Biography'
        self.urlbase = 'http://www.biographi.ca/en/bio/{id}E.html'
        self.hrtre = 'class="FirstParagraph">(.*?)</p>'
        self.language = 'en'

    def prepare(self, html):
        return html.replace('&amp;', '&').replace('&nbsp;', ' ')

    def findnames(self, html):
        return [self.TAGRE.sub('', x) for x in self.findallbyre('<strong>(.*)</strong>', html)]

    def finddescription(self, html):
        return self.TAGRE.sub('', self.findbyre('(?s)class="FirstParagraph">(.*?)(?:;|</p>)', html))

    def findlongtext(self, html):
        return self.findbyre('(?s)(<p id="paragraph.*?)<!--END BIBLIOGRAPHY', html)

    def findbirthdate(self, html):
        return self.findbyre(' b\. (\d+(?: \w+\.? \d+)?)', html)

    def findbirthplace(self, html):
        return self.findbyre(' b\. [^<>,]* (?:in|at) ([^<>,\.]*)', html, 'city')
    
    def finddeathdate(self, html):
        return self.findbyre(' d\. (\d+(?: \w+\.? \d+)?)', html)

    def finddeathplace(self, html):
        return self.findbyre(' d\. [^<>,]* (?:in|at) ([^<>,\.]*)', html, 'city')

    def findfather(self, html):
        return self.findbyre('(?:son|daughter) of ([^,;<>]*)', html, 'person')

    def findmother(self, html):
        return self.findbyre('(?:son|daughter) of [^;<>]*? and ([^,;<>]*)', html, 'person')

    def findspouses(self, html):
        return [self.findbyre(' m\. \d+(?: \w+ \d+)? ([^,;<>]+)', html, 'person')]


class IWDAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P2829'
        self.dbid = 'Q24045324'
        self.dbname = 'Internet Wrestling Database'
        self.urlbase = 'http://www.profightdb.com/wrestlers/{id}.html'
        self.hrtre = '(<table.*?)</table>'
        self.language = 'en'

    def getvalue(self, field, html, dtype=None):
        return self.findbyre('<strong>%s:</strong>(.*?)</td>'%field, html, dtype)

    def getvalues(self, field, html, dtype=None):
        section = self.getvalue(field, html)
        if section:
            return self.findallbyre('([^,]+)', section, dtype)
        else:
            return []

    def findinstanceof(self, html):
        return 'Q5'

    def findnames(self, html):
        return [
            self.getvalue('Name', html),
            self.getvalue('Preferred Name', html)
            ] +\
            self.getvalues('Ring Name\(s\)', html)

    def findbirthdate(self, html):
        return self.getvalue('Date Of Birth', html)

    def findnationalities(self, html):
        return self.getvalues('Nationality', html, 'country')

    def findbirthplace(self, html):
        return self.getvalue('Place Of Birth', html, 'city')

    def findgender(self, html):
        return self.getvalue('Gender', html, 'gender')


class BenezitAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P2843"
        self.dbid = "Q24255573"
        self.dbname = "Benezit"
        self.urlbase = "https://doi.org/10.1093/benz/9780199773787.article.{id}"
        self.hrtre = '(<h1.*?"moreLikeLink">)'
        self.language = 'en'

    def finddescription(self, html):
        return self.findbyre('"pf:contentName"\s*:\s*"(.*?)"', html)

    def findnames(self, html):
        return [self.findbyre('"pf:contentName"\s*:\s*"(.*?)[\("]', html)]

    def findlongtext(self, html):
        return self.findbyre('<abstract>(.*?)</abstract>', html)

    def findisntanceof(self, html):
        return "Q5"

    def findbirthdate(self, html):
        return self.findbyre('(?s)[^\w][bB]orn\s*((\w+\s*){,2}\d{4})[,\.\)]', html)

    def finddeathdate(self, html):
        return self.findbyre('(?s)[^\w][dD]ied\s*((\w+\s*){,2}\d{4})[,\.\)]', html)

    def findbirthplace(self, html):
        return self.findbyre('[bB]orn(?: [^<>,\.;]*,)? in ([^<>,\.;]*)', html, 'city')

    def finddeathplace(self, html):
        return self.findbyre('[dD]ied(?: [^<>,\.]*,)? in ([^<>,\.;]*)', html, 'city')

    def findoccupations(self, html):
        result = []
        section = self.findbyre('"pf:contentName" : "[^"]+-(.*?)"', html)
        if section:
            result += self.findallbyre('([^,]+)', section, 'occupation')
        section = self.findbyre('"pf:contentName" : "[^"]*\)(.*?)"', html)
        if section:
            result += self.findallbyre('([\s\w]+)', section, 'occupation')
        return result

    def findlastname(self, html):
        section = self.findbyre('"pf:contentName" : "([^"]+?),', html, 'lastname')

    def findfirstname(self, html):
        section = self.findbyre('"pf:contentName" : "[^",]+,\s*(\w+)', html, 'firstname')

    def findnationality(self, html):
        return self.findbyre('<abstract><p>([^<>]*?),', html, 'country')

    def findgender(self, html):
        return self.findbyre('<abstract><p>[^<>]*,([^<>,]*)\.</p>', html, 'gender')


class EcarticoAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P2915'
        self.dbid = 'Q24694883'
        self.dbname = 'ECARTICO'
        self.urlbase = 'http://www.vondel.humanities.uva.nl/ecartico/persons/{id}'
        self.hrtre = '(<h1.*?)<h2>References'
        self.language = 'en'

    def findnames(self, html):
        return self.findallbyre('<(?:h1|title)[^<>]*>(.*?)[<,\(]', html) +\
               self.findallbyre('alias:(.*?)<', html)

    def findinstanceof(self, html):
        return 'Q5'
    
    def findgender(self, html):
        return self.findbyre('schema:gender"[^<>]+resource="schema:([^<>]+?)"', html, 'gender') or\
               self.findbyre('Gender:</td><td[^<>]*>([^<>]+)', html, 'gender')

    def findbirthplace(self, html):
        return self.findbyre('schema:birthPlace"[^<>]*>(.*?)<', html, 'city')

    def finddeathplace(self, html):
        return self.findbyre('schema:deathPlace"[^<>]*>(.*?)<', html, 'city')

    def findbirthdate(self, html):
        return self.findbyre('schema:birthDate"[^<>]*>(?:<[^<>]*>)*([^<>]*)</time>', html)

    def finddeathdate(self, html):
        return self.findbyre('schema:deathDate"[^<>]*>(?:<[^<>]*>)*([^<>]*)</time>', html)

    def findspouses(self, html):
        return self.findallbyre('schema:spouse"[^<>]*>(.*?)[<\(]', html, 'person')

    def findfather(self, html):
        return self.findbyre('Father:.+schema:parent"[^<>]*>(.*?)[<\(]', html, 'person')
        
    def findmother(self, html):
        return self.findbyre('Mother:.+schema:parent"[^<>]*>(.*?)[<\(]', html, 'person')

    def findchildren(self, html):
        section = self.findbyre('(?s)<h2>Children:</h2>(.*?)<h', html)
        if section:
            return self.findallbyre('>([^<>]*?)(?:\([^<>]*)?</a>', section, 'person')

    def findoccupations(self, html):
        return self.findallbyre('schema:(?:hasOccupation|jobTitle)"[^<>]*>([^<>]*)</a>', html, 'occupation')

    def findworkplaces(self, html):
        return self.findallbyre('schema:(?:work)?[lL]ocation"[^<>]*>(.*?)<', html, 'city')
    
    def findstudents(self, html):
        return self.findallbyre('"ecartico:masterOf".*?>([^<>]*)</a>', html, 'person')

    def findteachers(self, html):
        return self.findallbyre('"ecartico:pupilOf".*?>([^<>]*)</a>', html, 'person')

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html) +\
               [('P245', self.findbyre('page/ulan/(\w+)', html))]

    def findgenres(self, html):
        return self.findallbyre('<td>Subject of[^<>]*</td>\s*<td>(.*?)<', html, 'genre') +\
               self.findallbyre('<td>Subject of[^<>]*</td>\s*<td>[^<>]+</td>\s*<td>(.*?)<', html, 'genre')


class RostochiensiumAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P2940"
        self.dbid = "Q1050232"
        self.dbname = "Catalogus Professorum Rostochiensium"
        self.urlbase = "http://cpr.uni-rostock.de/metadata/cpr_person_{id}"
        self.hrtre = '(<h2.*)<div class="docdetails-separator">.*?eingestellt'
        self.language = 'de'

    def finddescription(self, html):
        return self.findbyre('(?s)(<h2>.*?)<div class="docdetails-block">', html)

    def findlongtext(self, html):
        return self.findbyre('<div class="docdetails">(.*?)<div class="docdetails-label">eingestellt', html)

    def findnames(self, html):
        return self.findbyre('(?s)<title>(.*?)(?: - |<)', html)

    def findinstanceof(self, html):
        return "Q5"

    def findlastname(self, html):
        return self.findbyre('(?s)<h1>([^<>]*?),', html, 'lastname')

    def findfirstname(self, html):
        return self.findbyre('(?s)<h1>[^<>]*,\s*(\w+)', html, 'firstname')

    def finddegrees(self, html):
        return [self.findbyre('(?s)</h2>\s*</div><div class="docdetails-values">(.*?)<', html, 'degree')]

    def findemployers(self, html):
        return ["Q159895"]

    def findbirthdate(self, html):
        return self.findbyre('(?s)geboren\s*am\s*([\d\.]+)', html)

    def findbirthplace(self, html):
        return self.findbyre('(?s)geboren\s*am[^<>]*in(.*?)<', html, 'city')
    
    def finddeathdate(self, html):
        return self.findbyre('(?s)gestorben\s*am\s*([\d\.]+)', html)

    def finddeathplace(self, html):
        return self.findbyre('(?s)gestorben\s*am[^<>]*in(.*?)<', html, 'city')

    def findreligion(self, html):
        return self.findbyre('(?s)Konfession:.*?"docdetails-value">(.*?)<', html, 'religion')

    def findfather(self, html):
        return self.findbyre('(?s)>Vater</td>.*?<td[^<>]*>([^<>,\(]*)', html, 'person')

    def findmother(self, html):
        return self.findbyre('(?s)>Mutter</td>.*?<td[^<>]*>([^<>,\(]*)', html, 'person')

    def findschools(self, html):
        section = self.findbyre('(?s)>akademische  Abschlüsse:<.*?<tbody>(.*?)</tbody>', html)
        if section:
            return self.findallbyre(',(.*)', section, 'university')

    def findmemberships(self, html):
        section = self.findbyre('(?s)>wissenschaftliche\s*Mitgliedschaften:<.*?<tbody>(.*?)</tbody>', html)
        if section:
            return self.findallbyre('(?s)>(?:Korrespondierendes Mitglied, )?([^<>]*)<?td>\s*</tr>', section, 'organization')

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html)


class MunksRollAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P2941"
        self.dbid = "Q6936720"
        self.dbname = "Munk's Roll"
        self.urlbase = "http://munksroll.rcplondon.ac.uk/Biography/Details/{id}"
        self.hrtre = '<h2 class="PageTitle">(.*?)</div>'
        self.language = 'en'

    def findnames(self, html):
        return [self.findbyre('<h2 class="PageTitle">(.*?)<', html)]

    def finddescription(self, html):
        return self.findbyre('(?s)</h2>(.*?)<div', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)<div id="prose">(.*?)</div>', html)

    def findbirthdate(self, html):
        return self.findbyre('<p><em>b\.(.*?)(?: d\.|<)', html)

    def finddeathdate(self, html):
        return self.findbyre('<em>[^<>]* d\.(.*?)<', html)
    

class PlarrAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P2944'
        self.dbid = 'Q51726418'
        self.dbname = 'Royal College of Surgeons'
        self.urlbase = 'https://livesonline.rcseng.ac.uk/biogs/{id}.htm'
        self.language = 'en'
        self.hrtre = '(<div class="asset_detail" .*?(?:LIVES_DETAILS|RIGHTS_MGMT)">)'

    def findnames(self, html):
        return self.findallbyre('PERSON_NAME">(.*?)<', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)<div class="displayElementText LIVES_DETAILS">(.*?)</div>', html)

    def findbirthdate(self, html):
        return self.findbyre('LIVES_BIRTHDATE">(.*?)<', html)

    def finddeathdate(self, html):
        return self.findbyre('LIVES_DEATHDATE">(.*?)<', html)

    def findbirthplace(self, html):
        return self.findbyre('LIVES_BIRTHPLACE">(.*?)<', html, 'city')
    
    def finddeathplace(self, html):
        return self.findbyre('LIVES_DEATHPLACE">(.*?)<', html, 'city')

    def findoccupations(self, html):
        section = self.findbyre('(?s)LIVES_OCCUPATION">(.*?)</div>', html)
        if section:
            return self.findallbyre('(?:alt|title)="(.*?)"', section, 'occupation') 


class BookTradeAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P2945'
        self.dbid = 'Q25713895'
        self.dbname = 'British Book Trade'
        self.urlbase = 'http://bbti.bodleian.ox.ac.uk/details/?traderid={id}'
        self.hrtre = '(<table.*?</table>)'
        self.language = 'en'

    def getvalue(self, field, html, dtype=None):
        return self.findbyre('(?s)<strong>%s:</strong></td>\s*<td>(.*?)</td>'%field, html, dtype)

    def findnames(self, html):
        return [ self.getvalue('Name', html) ]

    def findlongtext(self, html):
        return self.getvalue('Notes', html)

    def findoccupations(self, html):
        result = []
        for section in [
                self.getvalue('Book Trades', html),
                self.getvalue('Non-Book Trade', html)
            ]:
            if section:
                result += self.findallbyre('([^,]*)', section, 'occupation')
        return result

    def finddeathdate(self, html):
        return self.findbyre('(\d+)\s*\(date of death\)', html)

    def findfloruitdata(self, html):
        section = self.getvalue('Trading Dates', html)
        if section:
            m = re.search('(\d{4})\s*(?:\(.*?\))?\s*-\s*(\d{4})', section)
            if m:
                return (m.group(1), m.group(2))
        return None

    def findfloruit(self, html):
        floruitdata = self.findfloruitdata(html)
        if floruitdata and floruitdata[0] == floruitdata[1]:
            return floruitdata[0]

    def findfloruitstart(self, html):
        floruitdata = self.findfloruitdata(html)
        if floruitdata and floruitdata[0] != floruitdata[1]:
            return floruitdata[0]
        
    def findfloruitend(self, html):
        floruitdata = self.findfloruitdata(html)
        if floruitdata and floruitdata[0] != floruitdata[1]:
            return floruitdata[1]

    def findworkplaces(self, html):
        return [ self.getvalue('Town', html, 'city') ]


class WikitreeAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P2949'
        self.dbid = 'Q1074931'
        self.dbname = 'WikiTree'
        self.urlbase = 'https://www.wikitree.com/wiki/{id}'
        self.hrtre = '<div class="ten columns">(.*?)<div class="SMALL"'
        self.language = 'en'

    def findnames(self, html):
        return [
            self.findbyre('<title>(.*?)[\(\|<]', html),
            self.findbyre('"keywords" content="([^"]+) genealogy', html),
            self.findbyre('<span itemprop="name">(.*?)<', html),
            ]

    def findlongtext(self, html):
        return self.findbyre('(?s)<a name="Biography">(.*?)<a name', html)

    def findfirstname(self, html):
        return self.findbyre('"givenName">(.*?)<', html, 'firstname')

    def findlastname(self, html):
        return self.findbyre('"familyName">(.*?)<', html, 'lastname')

    def findbirthdate(self, html):
        return self.findbyre('itemprop="birthDate" datetime="(\d{4})-00-00"', html) or\
               self.findbyre('itemprop="birthDate" datetime="(\d{4}-\d{2}-\d{2})"', html)

    def finddeathdate(self, html):
        return self.findbyre('itemprop="deathDate" datetime="(\d{4})-00-00"', html) or\
               self.findbyre('itemprop="deathDate" datetime="(\d{4}-\d{2}-\d{2})"', html)

    def findbirthplace(self, html):
        return self.findbyre('"birthPlace"[^<>]*>(?:<[^<>]*>)*([^<>]+)', html, 'city')
    
    def finddeathplace(self, html):
        return self.findbyre('"deathPlace"[^<>]*>(?:<[^<>]*>)*([^<>]+)', html, 'city')

    def findfather(self, html):
        return self.findbyre('(?s)"Father:[^"]+">(?:<[^<>]*>)*([^<>]+)', html, 'person')

    def findmother(self, html):
        return self.findbyre('(?s)"Mother:[^"]+">(?:<[^<>]*>)*([^<>]+)', html, 'person')

    def findchildren(self, html):
        return self.findallbyre('(?s)<span itemprop="children".*?><span itemprop="name">(.*?)<', html, 'person')

    def findspouses(self, html):
        return self.findallbyre('(?s)(?:Husband|Wife) of\s*(?:<[^<>]*>)*([^<>]+)', html, 'person')

    def findsiblings(self, html):
        section = self.findbyre('(?s)(?:Brother|Sister) of(.*?)</div>', html)
        if section:
            return self.findallbyre('>([^<>]*)</', section, 'person')
            
    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html, includesocial=False)

    def findfamily(self, html):
        section = self.findbyre('(?s)<div class="VITALS"><span class="large">(.*?)</div>', html)
        if section:
            return self.findbyre('itemprop="familyName" content="(.*?)"', section, 'family')


class GoodreadsAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P2963'
        self.dbid = None
        self.dbname = "Goodreads author"
        self.urlbase = 'https://www.goodreads.com/author/show/{id}'
        self.hrtre = '(<h1.*?)<div class="aboutAuthorInfo">'
        self.language = 'en'
        self.escapehtml = True

    def findinstanceof(self, html):
        return 'Q5'

    def findnames(self, html):
        return self.findallbyre("'([^']*)' property='[^']*title", html) +\
               self.findallbyre('"name">(.*?)<', html) +\
                [
                   self.findbyre('<title>([^<>\(\)]*)', html)
                ]

    def finddescriptions(self, html):
        return self.findallbyre('name="[^"]*description" content="(.*?)"', html) +\
               self.findallbyre("content='(.*?)' name='[^']*description", html)

    def findlongtext(self, html):
        return self.findbyre('(?s)<span id="freeTextauthor\d+"[^<>]*>(.*?)</span>', html) or\
               self.findbyre('(?s)<span id="freeTextContainerauthor\d+"[^<>]*>(.*?)</span>', html)

    def findbirthplace(self, html):
        return self.findbyre('(?s)Born</div>\s*(?:in )?(.*?)<', html, 'city')

    def findbirthdate(self, html):
        return self.findbyre("(?s)'birthDate'>(.*?)<", html)

    def finddeathdate(self, html):
        return self.findbyre("(?s)'deathDate'>(.*?)<", html)

    def findwebsite(self, html):
        section = self.findbyre('(?s)<div class="dataTitle">Website</div>(.*?)</div>', html)
        if section:
            return self.findbyre('>([^<>]*)</a>', section)

    def findgenres(self, html):
        return self.findallbyre('/genres/[^"\']*">(.*?)<', html, 'genre')
        
    def findmixedrefs(self, html):
        result = self.finddefaultmixedrefs(html)
        return [r for r in result if r[0] != 'P2969' and 'goodreads' not in r[1].lower() and r[1].lower() != 'intent']


class LbtAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P2977"
        self.dbid = "Q25935022"
        self.dbname = "Lord Byron and his Times"
        self.urlbase = "https://www.lordbyron.org/persRec.php?&selectPerson={id}"
        self.hrtre = '</style>(.*?</tr>.*?)</tr>'
        self.language = 'en'

    def findinstanceof(self, html):
        return 'Q5'

    def findnames(self, html):
        section = self.findbyre('(?s)<b>NAME AUTHORITIES:</b>(.*?)</td>', html)
        if section:
            return self.findallbyre('(?s)</b>([^<>]*)(?:, |\()\d', section)

    def finddescriptions(self, html):
        result = [ self.findbyre('(?s)<div[^<>]*font-size:\s*18px[^<>*>(.*?)[<;]', html) ]
        section = self.findbyre('(?s)<b>NAME AUTHORITIES:</b>(.*?)</td>', html)
        if section:
            result += self.findallbyre('(?s)</b>(.*?)<', section)
        return result
    
    def findlongtext(self, html):
        return self.findbyre('(?s)<div[^<>]*font-size:\s*18px[^<>]*>(.*?)</div>', html)

    def findbirthdate(self, html):
        return self.findbyre('<b>B/BAP:</b>(.*?)<', html)

    def finddeathdate(self, html):
        return self.findbyre('<b>DIED:</b>(.*?)<', html)

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html) +\
            [('P214', self.findbyre('<b>VIAF ID:</b>([^<>]*)', html)),
             ('P244', self.findbyre('<b>LOC ID:</b>([^<>]*)', html)),
             ]
        
    
class NationalArchivesAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P3029"
        self.dbid = None
        self.dbname = "The National Archives"
        self.urlbase = "https://discovery.nationalarchives.gov.uk/details/c/{id}"
        self.hrtre = '(<h1.*?)<h2'
        self.language = 'en'

    def findnames(self, html):
        return [self.findbyre('<title>([^<>]*)\(', html)]

    def finddescription(self, html):
        return self.findbyre('<title>(.*?)[\|<]', html)

    def findgender(self, html):
        return self.findbyre('(?s)Gender:</th>.*?<td[^<>]*>(.*?)<', html, 'gender')

    def findfirstname(self, html):
        return self.findbyre('(?s)Forenames:</th>.*?<td[^<>]*>\s*(\w*)', html, 'firstname')

    def findlastname(self, html):
        return self.findbyre('(?s)Surname:</th>.*?<td[^<>]*>(.*?)<', html, 'lastname')

    def findbirthdate(self, html):
        return self.findbyre('(?s)Date:</th>.*?<td[^<>]*>([^<>-]*)-', html)

    def finddeathdate(self, html):
        return self.findbyre('(?s)Date:</th>.*?<td[^<>]*>[^<>]*-(.*?)<', html)

    def findoccupations(self, html):
        section = self.findbyre('\)([^<>]+)</h1>', html)
        if section:
            result = []
            parts = self.findallbyre('[\w\s]+', section)
            for part in parts:
                result += [self.getdata('occupation', p) for p in part.split(' and ')]
            return result

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html, includesocial=False)


class LdifAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P3107"
        self.dbid = "Q1822317"
        self.dbname = "Lexicon of International Films"
        self.urlbase = "https://www.zweitausendeins.de/filmlexikon/?sucheNach=titel&wert={id}"
        self.hrtre = "<div class='film-detail'>(.*?)<div class="
        self.language = 'de'

    def findnames(self, html):
        return self.findallbyre("class='[^'<>]*-o?titel'>(.*?)<", html) +\
               self.findallbyre("<b>Originaltitel: </b>(.*?)<", html)

    def findlongtext(self, html):
        return self.findbyre("(?s)<div class='film-detail'>(.*?)</div>", html)

    def findgenres(self, html):
        sections = self.findallbyre("'film-angaben'>([^<>]+)</p>", html)
        result = []
        for section in sections:
            result += [self.getdata('genre', genre) for genre in section.split(',')]
        return result

    def findorigcountries(self, html):
        section = self.findbyre("<b>Produktionsland:\s*</b>(.*?)<", html)
        if section:
            return self.findallbyre("([^/]+)", section, 'country')

    def findpubdate(self, html):
        return self.findbyre("<b>Produktionsjahr:\s*</b>(.*?)<", html)
        
    def findprodcoms(self, html):
        return [self.findbyre("<b>Produktionsfirma:\s*</b>(.*?)<", html, 'filmcompany')]

    def finddurations(self, html):
        return [self.findbyre("<b>Länge:\s*</b>(.*?)<", html)]

    def findcast(self, html):
        section = self.findbyre("(?s)<b>Darsteller:\s*</b>(.*?)</p>", html)
        if section:
            return self.findallbyre(">([^<>]*)</a>", section, 'actor')
        
    def findproducers(self, html):
        section = self.findbyre("(?s)<b>Produzent:\s*</b>(.*?)</p>", html)
        if section:
            return self.findallbyre(">([^<>]*)</a>", section, 'filmmaker')
        
    def findmoviedirectors(self, html):
        section = self.findbyre("(?s)<b>Regie:\s*</b>(.*?)</p>", html)
        if section:
            return self.findallbyre(">([^<>]*)</a>", section, 'filmmaker')
        
    def findscreenwriters(self, html):
        section = self.findbyre("(?s)<b>Drehbuch:\s*</b>(.*?)</p>", html)
        if section:
            return self.findallbyre(">([^<>]*)</a>", section, 'filmmaker')

    def finddirectorsphotography(self, html):
        section = self.findbyre("(?s)<b>Kamera:\s*</b>(.*?)</p>", html)
        if section:
            return self.findallbyre(">([^<>]*)</a>", section, 'filmmaker')

    def findcomposers(self, html):
        section = self.findbyre("(?s)<b>Musik:\s*</b>(.*?)</p>", html)
        if section:
            return self.findallbyre(">([^<>]*)</a>", section, 'composer')

    def findmovieeditors(self, html):
        section = self.findbyre("(?s)<b>Schnitt:\s*</b>(.*?)</p>", html)
        if section:
            return self.findallbyre(">([^<>]*)</a>", section, 'filmmaker')   

class PeakbaggerAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P3109"
        self.dbid = "Q28736250"
        self.dbname = "Peakbagger"
        self.urlbase = "http://www.peakbagger.com/peak.aspx?pid={id}"
        self.hrtre = '(<h1>.*?)<address>'
        self.language = 'en'

    def finddescriptions(self, html):
        return [
            self.findbyre('(?s)(<h1.*?</h2>)', html),
            self.findbyre('(?s)(<h1.*?</h1>)', html)
            ]

    def findnames(self, html):
        return [self.findbyre('<title>([^<>]*) - ', html)]

    def findinstanceof(self, html):
        return "Q8502"

    def findelevations(self, html):
        result = self.findbyre('Elevation:(.+?)<', html)
        if result:
            return [r for r in result.split(",") if not '+' in result]

    def findcoords(self, html):
        return self.findbyre('>([^<>]+) \(Dec Deg\)', html)

    def findcountry(self, html):
        return self.findbyre('Country</td><td>(.*?)</td>', html, 'country')

    def findadminloc(self, html):
        result = self.findbyre('County/Second Level Region</td><td>(.*?)</td>', html, 'county')
        return result or self.findbyre('State/Province</td><td>(.*?)</td>', html, 'state')
        
    def findprominences(self, html):
        result = self.findbyre('Prominence:(.*?)</td>', html)
        if result:
            return result.split(",")

    def findisolations(self, html):
        result = self.findbyre('True Isolation:(.*?)<', html)
        if result:
            return result.split(",")

    def findmountainrange(self, html):
        results = self.findallbyre('Range\d+:\s*(?:<.*?>)?([^<>]+)<', html)
        if results:
            return self.getdata('mountainrange', results[-1])


class OfdbAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P3138"
        self.dbid = "Q1669874"
        self.dbname = "Online-Filmdatenbank"
        self.urlbase = "https://ssl.ofdb.de/film/{id},"
        self.urlbase3 = 'https://ssl.ofdb.de/view.php?page=film_detail&fid={id}'
        self.hrtre = 'Filmangaben(.*?)<!-- Inhaltsangabe -->'
        self.language = 'de'
        self.escapeunicode = True

    def finddescriptions(self, html):
        return [
            self.findbyre('(?s)<!-- Rechte Spalte -->(.*?<tr.*?<tr.*?<tr.*?<tr.*?)<tr', html),
            self.findbyre('(?s)<!-- Rechte Spalte -->(.*?<tr.*?<tr.*?<tr.*?)<tr', html),
            self.findbyre('(?s)<!-- Rechte Spalte -->(.*?<tr.*?<tr.*?)<tr', html),
            ]

    def findnames(self, html):
        result = [self.findbyre('"og:title" content="(.*?)[\("]', html)]
        section = self.findbyre('(?s)Alternativtitel:(.*?)</table>', html)
        if section:
            result += self.findallbyre('<b>(.*?)<', section)
        return result

    def findinstanceof(self, html):
        return "Q11424"

    def findpubdate(self, html):
        return self.findbyre('(?s)Erscheinungsjahr:.*?>(\d+)</a>', html)

    def findorigcountry(self, html):
        return self.findbyre('(?s)Herstellungsland:.*?>([^<>]+)</a>', html, 'country')

    def findmoviedirectors(self, html):
        directorlist = self.findbyre('(?s)(Regie:.*?)</tr>', html)
        if directorlist:
            return self.findallbyre('>([^<>]+)</span', directorlist, 'filmmaker')

    def findcast(self, html):
        castlist = self.findbyre('(?s)(Darsteller:.*?)</tr>', html)
        if castlist:
            return self.findallbyre('>([^<>]+)</span', castlist, 'actor')

    def findgenres(self, html):
        genrelist = self.findbyre('(?s)(Genre\(s\):.*?)</tr>', html)
        if genrelist:
            return self.findallbyre('>([^<>]+)</span', genrelist, 'genre')

    def findscreenwriters(self, html):
        section = self.findbyre('(?s)<i>Drehbuchautor\(in\)</i>.*?(<table>.*?</table>)', html)
        if section:
            return self.findallbyre('<b>([^<>]*)</b>', section, 'filmmaker')

    def findcomposers(self, html):
        section = self.findbyre('(?s)<i>Komponist\(in\)</i>.*?(<table>.*?</table>)', html)
        if section:
            return self.findallbyre('<b>([^<>]*)</b>', section, 'filmmaker')

    def finddirectorsphotography(self, html):
        section = self.findbyre('(?s)<i>Director of Photography \(Kamera\)</i>.*?(<table>.*?</table>)', html)
        if section:
            return self.findallbyre('<b>([^<>]*)</b>', section, 'filmmaker')

    def findmovieeditors(self, html):
        section = self.findbyre('(?s)<i>Cutter \(Schnitt\)</i>.*?(<table>.*?</table>)', html)
        if section:
            return self.findallbyre('<b>([^<>]*)</b>', section, 'filmmaker')


class RunebergAuthorAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P3154"
        self.dbid = "Q933290"
        self.dbname = "Project Runeberg"
        self.urlbase = "http://runeberg.org/authors/{id}.html"
        self.hrtre = '<br clear=all>(.*?)<p>Project'
        self.language = 'en'
        self.escapeunicode = True

    def finddescription(self, html):
        return self.findbyre('(?s)<br clear=all>(.*?)<p>', html)

    def findnames(self, html):
        return [self.findbyre('<title>(.*?)</title>', html)]

    def findlongtext(self, html):
        return self.findbyre('(?s)</h1>(.*?)<a', html)

    def findinstanceof(self, html):
        return "Q5"

    def findlastname(self, html):
        return self.findbyre('(?s)<b>([^<>]*),', html, 'lastname')

    def findfirstname(self, html):
        return self.findbyre('(?s)<b>[^<>]*,\s*(\w+)', html, 'firstname')

    def findbirthdate(self, html):
        return self.findbyre('(?s)<b>[^<>]+\(([^<>\(\)]*?)-', html)

    def finddeathdate(self, html):
        return self.findbyre('(?s)<b>[^<>]+\([^<>\(\)]+-([^<>\(\)]*)', html)

    def findoccupations(self, html):
        return [self.findbyre('(?s)<br clear=all>.*?</b>\s*,([^<>]*?),', html, 'occupation')]

    def findnationality(self, html):
        return self.findbyre('(?s)<br clear=all>.*?</b>[^<>]*,([^<>]*?)\.', html, 'country')

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html, includesocial=False)
    

class UGentAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P3159"
        self.dbid = "Q26453893"
        self.dbname = "UGent Memorialis"
        self.urlbase = "http://www.ugentmemorialis.be/catalog/{id}"
        self.hrtre = '(<h3.*?</dl>)'
        self.language = 'nl'

    def finddescription(self, html):
        return self.findbyre('<title>(.*?)[\|<]', html)

    def findnames(self, html):
        return [self.findbyre('<title>(.*?)\d{4}\s*-', html)]

    def findlongtext(self, html):
        return self.findbyre('(?s)(<h3.*?</dl>)', html)
    
    def findinstanceof(self, html):
        return "Q5"

    def findbirthdate(self, html):
        return self.findbyre('<dd class="blacklight-birth_date_display">[^<>]*?([^<>,]*?)</dd>', html)

    def findbirthplace(self, html):
        return self.findbyre('<dd class="blacklight-birth_date_display">([^<>,]*),', html, 'city')

    def finddeathdate(self, html):
        return self.findbyre('<dd class="blacklight-death_date_display">[^<>]*?([^<>,]*?)</dd>', html)

    def finddeathplace(self, html):
        return self.findbyre('<dd class="blacklight-death_date_display">([^<>,]*),', html, 'city')

    def findemployers(self, html):
        return ["Q1137665"]

    def findschools(self, html):
        section = self.findbyre('<dd class="blacklight-higher_education_display">(.*?)</dd>', html)
        if section:
            return self.findallbyre('([^<>]{3,})', section, 'university')

    def findviaf(self, html):
        return self.findbyre('"http://viaf.org/viaf/(\w+)"', html)


class BandcampAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P3283"
        self.dbid = None
        self.dbname = 'Bandcamp'
        self.urlbase = 'https://{id}.bandcamp.com/'
        self.language = 'en'
        self.hrtre = '()'

    def findnames(self, html):
        return [
            self.findbyre('<title>([^<>]+)\|', html),
            self.findbyre('"og_site_name" content="(.*?)"', html),
            self.findbyre('"og_title" content="(.*?)"', html)
            ]

    def findlongtext(self, html):
        return self.findbyre('(?s)<meta name="Description" content="(.*?)"', html)

    def findmixedrefs(self, html):
        section = self.findbyre('(?s)<ol id="band-links">(.*?)</ol>', html) or html
        return self.finddefaultmixedrefs(section)


class HkmdbAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P3346"
        self.dbid = 'Q5369036'
        self.dbname = 'Hong Kong Movie Database'
        self.urlbase = 'http://www.hkmdb.com/db/people/view.mhtml?id={id}'
        self.language = 'en'
        self.hrtre = '(<TABLE WIDTH="90%".*?)<TABLE CELLPADDING="3"'

    def findlanguagenames(self, html):
        result = [('en', name) for name in self.findallbyre('(?s)<font size="[^"]+"><b>(.*?)[<\(]', html)] +\
                 [('zh', name) for name in self.findallbyre('(?s)<font size="[^"]+"><b>(.*?)[<\(]', html)]
        section = self.findbyre('(?s)Aliases:(.*?<TR>)', html)
        if section:
            section = section.replace("&nbsp;", ' ')
            result += [('en', name) for name in self.findallbyre('(?s)>(.*?)[,<]', section)]
        return result

    def findbirthdate(self, html):
        return self.findbyre('Born: (.*?)<', html)

    def findoccupations(self, html):
        return self.findallbyre('(?s)<TD COLSPAN="\d+">([^<>]+)<i>\([^<>]*\)</i></TD>', html, 'occupation')


class NobelPrizeAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P3360'
        self.dbid = None
        self.dbname = 'Nobel Prize Nominations'
        self.urlbase = 'https://www.nobelprize.org/nomination/archive/show_people.php?id={id}'
        self.hrtre = '(<div id="main">.*?)<b>'
        self.language = 'en'

    def findnames(self, html):
        return [self.findbyre('<h2>(.*?)</', html)]

    def findlastname(self, html):
        return self.findbyre('Lastname/org:(?:<[^<>]*>)*([^<>]+)', html, 'lastname')

    def findfirstname(self, html):
        return self.findbyre('Firstname:(?:<[^<>]*>)*([^<>]+)', html, 'firstname')

    def findgender(self, html):
        return self.findbyre('Gender:(?:<[^<>]*>)*([^<>]+)', html, 'gender')

    def findbirthdate(self, html):
        return self.findbyre('Year, Birth:(?:<[^<>]*>)*([^<>]+)', html)
        
    def finddeathdate(self, html):
        return self.findbyre('Year, Death:(?:<[^<>]*>)*([^<>]+)', html)
        

class SurmanAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P3392'
        self.dbid = None
        self.dbname = 'Surman Index'
        self.urlbase = 'https://surman.english.qmul.ac.uk/main.php?personid={id}'
        self.hrtre= '"detailDisplay">.*?<br/>(.*?)<strong>Notes:'
        self.language = 'en'

    def findnames(self, html):
        return [self.findbyre('(?s)<h2>(.*?)</', html)]

    def findlongtext(self, html):
        return self.findbyre('(?s)"detailDisplay">.*?<br/>(.*?<strong>Notes:.*?)<br', html)

    def findinstanceof(self, html):
        return 'Q5'

    def findbirthdate(self, html):
        return self.findbyre('(?s)<strong>Born:\s*</strong>([^<>]*?\d{4})', html)

    def findbirthplace(self, html):
        return self.findbyre('(?s)<strong>Born:\s*</strong>[^<>]*?\d{4}([^<>]*)', html, 'city')
        
    def finddeathdate(self, html):
        return self.findbyre('(?s)<strong>Died:\s*</strong>([^<>]*?\d{4})', html)

    def finddeathplace(self, html):
        return self.findbyre('(?s)<strong>Died:\s*</strong>[^<>]*?\d{4}([^<>]*)', html, 'city')
        
    def findschools(self, html):
        section = self.findbyre('(?s)<strong>Education:\s*</strong>(.*?)</table>', html)
        if section:
            return self.findallbyre('(?s)<a[^<>]*>(.*?)<', section, 'university')

    def findworkplaces(self, html):
        section = self.findbyre('(?s)<strong>Career:\s*</strong>(.*?)</table>', html)
        if section:
            return self.findallbyre('(?s)parishid=[^<>]*>(.*?)<', section, 'city')

    def findoccupations(self, html):
        return ['Q2259532']

    def findreligion(self, html):
        return 'Q1062789'


class CcedAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P3410'
        self.dbid = None
        self.dbname = 'Clergy of the Church of England database'
        self.urlbase = 'http://db.theclergydatabase.org.uk/jsp/persons/DisplayPerson.jsp?PersonID={id}'
        self.hrtre = '<h2>Ordination Events</h2>()</body>'
        self.language = 'en'

    def findnames(self, html):
        return self.findallbyre('(?s)<tr[^<>]*>\s*<td>[^<>]*</td>\s*<td>([^<>]*[a-z][^<>]*)', html)

    def findfirstname(self, html):
        return self.findbyre('(?s)<tr[^<>]*>\s*<td>[^<>]*</td>\s*<td>[^<>]+,([^<>]*)', html, 'firstname')

    def findlastname(self, html):
        return self.findbyre('(?s)<tr[^<>]*>\s*<td>[^<>]*</td>\s*<td>([^<>]+),', html, 'lastname')     

    def findlongtext(self, html):
        return self.findbyre('(?s)<h3>Comments</h3>(.*?)<h\d', html)

    def findschools(self, html):
        section = self.findbyre('(?s)<h2>Education Events</h2>(.*?)<h2', html)
        if section:
            return self.findallbyre('(?s)<tr[^<>]*>\s*<td>[^<>]*</td>\s*<td>[^<>]*</td>\s*<td>[^<>]*</td>\s*<td>[^<>]</td>\s*<td>([^<>]*)', section, 'university')

    def finddegrees(self, html):
        section = self.findbyre('(?s)<h2>Education Events</h2>(.*?)<h2', html)
        if section:
            return self.findallbyre('(?s)<tr[^<>]*>\s*<td>[^<>]*</td>\s*<td>[^<>]*</td>\s*<td>[^<>]*</td>\s*<td>([^<>]*)', section, 'degree')

    def findinstanceof(self, html):
        return 'Q5'

    def findoccupations(self, html):
        return ['Q2259532']

    def findreligion(self, html):
        return 'Q82708'

    def findpositions(self, html):
        section = self.findbyre('(?s)<h2>Appointment Events</h2>(.*?)<h2', html)
        if section:
            return self.findallbyre('(?s)<tr[^<>]*>\s*<td>[^<>]*</td>\s*<td>[^<>]*</td>\s*<td>[^<>]*</td>\s*<td>([^<>]*)', section, 'position')

    def findbirthdate(self, html):
        section = self.findbyre('(?s)<h2>Birth Events</h2>(.*?)<h2', html)
        if section:
            return self.findbyre('(?s)<tr[^<>]*>\s*<td>\s*(\d*[1-9]\d*/\d+/\d+)\s*<', html)

    def findbirthplace(self, html):
        section = self.findbyre('(?s)<h2>Birth Events</h2>(.*?)<h2', html)
        if section:
            for city in self.findallbyre('(?s)<tr[^<>]*>\s*<td>[^<>]*</td>\s*<td>([^<>]*)</td>', section, 'city'):
                if city:
                    return city

    def findworkplaces(self, html):
        section = self.findbyre('(?s)<h2>Appointment Events</h2>(.*?)<h2', html)
        if section:
            return self.findallbyre('<a href="../locations[^<>]+>(.*?)<', html, 'city')
        

class EnlightenmentAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P3429"
        self.dbid = "Q1326050"
        self.dbname = "Electronic Enlightenment"
        self.urlbase = "http://www.e-enlightenment.com/person/{id}/"
        self.hrtre = '</h1>.*?</h2>(.*?)<h[3r]'
        self.language = 'en'

    def findnames(self, html):
        return [self.findbyre('(?s)Name</span>\s*:?\s*(.*?)<', html)]

    def finddescription(self, html):
        result = self.findbyre('(?s)Occupation</span>(.*?)<p>', html)
        if result:
            return self.TAGRE.sub('', result).lstrip(':')

    def findlongtext(self, html):
        return self.findbyre('(?s)<div id="content">(.*?)</div>', html)

    def findinstanceof(self, html):
        return 'Q5'

    def findbirthdate(self, html):
        section = self.findbyre('(?s)Dates</span>(.*?)<p>', html)
        if section:
            return self.findbyre('born ([\w\s]+)', section)

    def finddeathdate(self, html):
        section = self.findbyre('(?s)Dates</span>(.*?)<p>', html)
        if section:
            return self.findbyre('died ([\w\s]+)', section)

    def findnationality(self, html):
        return self.findbyre('(?s)Nationality</span.*?>([^<>]*)</a>', html, 'country')

    def findoccupations(self, html):
        section = self.findbyre('(?s)Occupation</span>(.*?)<p>', html)
        if section:
            return self.findallbyre('>([^<>]*)</a>', section, 'occupation')

    def findinception(self, html):
        section = self.findbyre('(?s)Dates</span>(.*?)<p>', html)
        if section:
            return self.findbyre('founded ([\w\s]+)', section)

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html)


class SnacAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P3430'
        self.dbid = 'Q29861311'
        self.dbname = 'SNAC'
        self.urlbase = 'http://snaccooperative.org/ark:/99166/{id}'
        self.hrtre = '(<div class="main_content">.*?)<div class="relations"'
        self.language = 'en'

    def findnames(self, html):
        section = self.findbyre('(?s)extra-names[^<>]*"[^<>]*>(.*?)<div class="', html)
        if section:
            return self.findallbyre('<div>(.*?)<', section)

    def finddescriptions(self, html):
        description = self.findbyre('(?s)"og:description"[^<>]*content="(.*?)"', html)
        if description:
            description = re.sub('(?s)\s+', ' ', description)
            result = [ description, description.split('.')[0]]
        else:
            result = []
        result += self.findallbyre('(?s)<p xmlns="[^<>"]*">(.*?)<', html)
        return result

    def findlongtext(self, html):
        return self.findbyre('(?s)<biogHist>(.*?)</biogHist>', html)

    def findbirthdate(self, html):
        return self.findbyre('>Birth(.*?)<', html)

    def finddeathdate(self, html):
        return self.findbyre('>Death(.*?)<', html)

    def findnationalities(self, html):
        section = self.findbyre('(?s)Nationality:\s*<[^<>]*>([^<>]*)<', html)
        if section:
            return self.findallbyre('([\w\s]+)', section, 'country')

    def findlanguagesspoken(self, html):
        section = self.findbyre('(?s)Language:\s*<[^<>]*>([^<>]*)<', html)
        if section:
            return self.findallbyre('([\w\s]+)', section, 'language')

    def findoccupations(self, html):
        section = self.findbyre('(?s)<h4>Occupations:</h4>(.*?)(?:</ul>|<h4>)', html)
        if section:
            return self.findallbyre('<li>([^<>]*)<', section, 'occupation')
        

class BabelioAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P3630"
        self.dbid = "Q2877812"
        self.dbname = "Babelio"
        self.urlbase = "https://www.babelio.com/auteur/-/{id}"
        self.hrtre = '(<div class="livre_bold">.*?>)Ajouter'
        self.language = 'fr'
        self.escapeunicode = True

    def finddescription(self, html):
        return self.findbyre('<meta name="description" content="(.*?)"', html)

    def findnames(self, html):
        return [self.findbyre('<title>(.*?)(?:\(| - |<)', html)]

    def findlongtext(self, html):
        return self.findbyre('(?s)<div id="d_bio"[^<>]*>(.*?)</div>', html)

    def findinstanceof(self, html):
        return "Q5"

    def findnationality(self, html):
        return self.findbyre('(?s)Nationalit[^<>]*:(.*?)<', html, 'country')

    def findbirthplace(self, html):
        return self.findbyre('N[^\s]*e\) [^\s]+ :([^<>]*),', html, 'city')

    def finddeathplace(self, html):
        return self.findbyre('Mort\(e\) [^\s]+ :([^<>]*),', html, 'city')

    def findbirthdate(self, html):
        return self.findbyre('itemprop="birthDate">(.*?)<', html)
        
    def finddeathdate(self, html):
        return self.findbyre('itemprop="deathDate">(.*?)<', html)

    def findwebsite(self, html):
        return self.findbyre("(?s)[Ss]ite(?: [\w\s\-]*)?:(?:<br />)?([^<>]*://[^<>]*)", html)


class ArtnetAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P3782"
        self.dbid = "Q266566"
        self.dbname = "Artnet"
        self.urlbase = "http://www.artnet.com/artists/{id}/"
        self.urlbase3 = "http://www.artnet.com/artists/{id}/biography"
        self.hrtre = '(<h1.*?</section>)'
        self.language = 'en'

    def finddescription(self, html):
        return self.findbyre('<div class="headline">(.*?)</div>', html)

    def findlongtext(self, html):
        parts = self.findallbyre('(?s)(<div class="bioSection.*?)</div>', html)
        return '\n'.join(parts)

    def findnames(self, html):
        return [self.findbyre("'artistName'\s*:\s*'(.*?)'", html)]

    def findinstanceof(self, html):
        return "Q5"

    def findnationalities(self, html):
        section = self.findbyre('"nationality":"(.*?)"', html)
        if section:
            return self.findallbyre('([^/,\.;]+)', section, 'country')

    def findbirthdate(self, html):
        return self.findbyre('"birthDate":"(.*?)"', html)

    def finddeathdate(self, html):
        return self.findbyre('"deathDate":"(.*?)"', html)

    def findincollections(self, html):
        result = []
        section = self.findbyre('(?s)Public Collections</h2>(.*?)</div>', html)
        result += self.findallbyre('>([^<>]*?)<', section or '', 'museum')
        section = self.findbyre('(?s)Collections:(.*?)</dl>', html)
        result += self.findallbyre('>([^<>]*?)<', section or '', 'museum')
        section = self.findbyre('(?s)Museums:(.*?)</dl>', html)
        result += self.findallbyre('>([^<>]*?)<', section or '', 'museum')
        return result

    def findmemberships(self, html):
        return self.findallbyre('(?s)>Member (.*?)<', html, 'organization')


class DanskefilmAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P3786'
        self.dbid = 'Q5159753'
        self.dbname = 'Danskefilm'
        self.urlbase = 'https://danskefilm.dk/skuespiller.php?id={id}'
        self.hrtre = '(<div class="col-lg-4 col-md-4">.*?</div>)'
        self.language = 'da'
        self.escapeunicode = True

    def findnames(self, html):
        return [
            self.findbyre('<title>(.*?)(?: - |<)', html),
            self.findbyre('<H4><B>(.*?)<', html)
            ]

    def findlongtext(self, html):
        return self.findbyre('(?s)<div class="biografi">(.*?)</div>', html)

    def finddescriptions(self, html):
        return [
            self.findbyre('"description" content="(.*?)"', html),
            self.findbyre('Biografi(?:<[^<>]*>)*(.*?)[<\.]', html)
            ]

    def findbirthdate(self, html):
        return self.findbyre('Født: ([\d\-]+)', html)

    def findbirthplace(self, html):
        return self.findbyre('Født:[^<>]* i (.*?)<', html, 'city')
    
    def finddeathdate(self, html):
        return self.findbyre('Død: ([\d\-]+)', html)

    def finddeathplace(self, html):
        return self.findbyre('Død:[^<>]* i (.*?)<', html, 'city')
    
    def findburialplace(self, html):
        return self.findbyre('Gravsted:(.*?)<', html, 'cemetery')

    def findawards(self, html):
        section = self.findbyre('(?s)(<B>Priser.*?</table>)', html)
        if section:
            return self.findallbyre('(?s)<td>(.*?)[\(<]', section, 'award')


class BnaAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P3788'
        self.dbid = None
        self.dbname = 'National Library of the Argentine Republic'
        self.urlbase = 'https://catalogo.bn.gov.ar/F/?func=direct&doc_number={id}&local_base=BNA10'
        self.hrtre = '<!-- filename: full-999-body-bna10 -->(.*)<!-- filename: full-999-body-bna10 -->'
        self.language = 'es'

    def getvalue(self, field, html, dtype=None):
        return self.findbyre('(?s)<td class="td1"[^<>]*>\s*<strong>%s</strong>\s*</td>\s*<td[^<>]*>(.*?)</td>'%field, html, dtype)

    def getvalues(self, field, html, dtype=None):
        section = self.getvalue(field, html)
        if section:
            return self.findallbyre('(?s)>(.*?)<', '>' + section + '<', dtype)
        else:
            return []

    def prepare(self, html):
        return html.replace('&nbsp;', ' ')

    def instanceof(self, html):
        return 'Q5'

    def findnames(self, html):
        result = []
        section = self.getvalue('Nombre personal', html)
        if section:
            result += self.findallbyre('>([^<>,]*,[^<>,]*),', section)
        result += self.getvalues('Forma compl. nombre', html)
        return result

    def finddescription(self, html):
        return self.getvalue('Datos biogr./hist.', html)

    def findlongtext(self, html):
        return (self.getvalue('Datos biogr./hist.', html) or '') + ' ' + (self.getvalue('Fuente de info.', html) or '')

    def findbirthdate(self, html):
        section = self.getvalue('Nombre personal', html)
        if section:
            return self.findbyre(',([^<>\-,]*)-[^<>\-,]*<', section)

    def finddeathdate(self, html):
        section = self.getvalue('Nombre personal', html)
        if section:
            return self.findbyre(',[^<>]*-([^<>\-,]*)<', section)

    def findbirthplace(self, html):
        return self.findbyre('Nació en([^<>]*)', html, 'city')

    def finddeathplace(self, html):
        return self.findbyre('Murió en([^<>]*)', html, 'city')

    def findworkfields(self, html):
        return self.getvalues('Campo de actividad', html, 'subject')

    def findoccupations(self, html):
        return self.getvalues('Ocupación', html, 'occupation')

    def findmemberships(self, html):
        return self.getvalues('Grupos asociados', html, 'organization')

    def findgender(self, html):
        return self.getvalue('Sexo', html, 'gender')

    def findlanguages(self, html):
        return self.getvalues('Idiomas asociados', html, 'language')


class AnimeConsAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P3790'
        self.dbid = 'Q74763172'
        self.dbname = 'AnimeCons'
        self.urlbase = 'https://animecons.com/guests/bio/{id}/'
        self.hrtre = '<p class="lead">(.*?)<p><b>'
        self.language = 'en'

    def finalscript(self, html):
        return self.findbyre('(?s).*<script type="application/ld\+json">(.*?)</script>', html)

    def findinstanceof(self, html):
        return self.findbyre('"@type": "(.*?)"', self.finalscript(html), 'instanceof')

    def findnames(self, html):
        return [self.findbyre('"name": "(.*?)"', self.finalscript(html))]

    def finddescription(self, html):
        return self.findbyre('"jobTitle": "(.*?)"', self.finalscript(html))

    def findlongtext(self, html):
        return self.findbyre('(?s)<b>Biography:</b>(.*?)></div>', html)

    def findnationality(self, html):
        return self.findbyre('"addressCountry": "(.*?)"', self.finalscript(html), 'country')

    def findoccupations(self, html):
        section = self.findbyre('"jobTitle": "(.*?)"', self.finalscript(html))
        if section:
            return self.findallbyre('([\w\s]+)', section, 'occupation')

    def findwebsite(self, html):
        return self.findbyre('"url": "(.*?)"', self.finalscript(html))


class PublonsAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P3829'
        self.dbid = 'Q18389628'
        self.dbname = 'Publons'
        self.urlbase = 'https://publons.com/researcher/{id}/'
        self.urlbase3 = 'https://publons.com/researcher/api/{id}/summary/'
        self.urlbase4 = 'https://publons.com/researcher/api/{id}/summary-publications/'
        self.hrtre = '()'
        self.language = 'en'

    def findnames(self, html):
        return [
            self.findbyre('href="[^"]*/%s/[^"]*">(.*?)<'%self.id, html),
            self.findbyre('<title>([^<>\|]*)', html)
            ]

    def finddescription(self, html):
        return self.findbyre('"blurb":"(.*?)"', html)

    def findworkfields(self, html):
        return self.findallbyre('research_field=\d+","name":"(.*?)"', html, 'subject')

    def findemployers(self, html):
        results = self.findallbyre('institution/\d+/","name":"(.*?)"', html)
        results = [result for result in results if 'student' not in result.lower().strip().split('-')[0]]
        results = [result.split(',')[-1] for result in results]
        results = [result.split('from')[0].split('until')[0] for result in results]
        results = '@'.join(results)
        return self.findallbyre('([^@]+)', results, 'university')

    def findschools(self, html):
        results = self.findallbyre('institution/\d+/","name":"(.*?)"', html)
        results = [result for result in results if 'student' in result.lower().strip().split('-')[0]]
        results = [result.split(',')[-1] for result in results]
        results = [result.split('from')[0].split('until')[0] for result in results]
        results = '@'.join(results)
        return self.findallbyre('([^@]+)', results, 'university')

    def findwebpages(self, html):
        section = self.findbyre('"affiliations":\[(.*?)\]', html)
        if section:
            return self.findallbyre('"url":"(.*?)"', section)

    def findnotableworks(self, html):
        html = re.sub('("journal":\{(.*?)\})', '', html)
        preresults = self.findallbyre('"title":"(.*?)"', html)
        preresults = preresults[:3]
        return [self.findbyre('(.*)', preresult, 'work') for preresult in preresults]
        

class SynchronkarteiAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P3844'
        self.dbid = 'Q1204237'
        self.dbname = 'Deutsche Synchronkartei'
        self.urlbase = 'https://www.synchronkartei.de/film/{id}'
        self.hrtre = '(<h1.*?)<div class="alert'
        self.language = 'de'

    def findnames(self, html):
        return [
            self.findbyre('<h1>(.*?)<', html),
            self.findbyre('<h3>(.*?)<', html),
            ]

    def description(self, html):
        return self.findbyre('<div><p>(.*?)<', html)

    def findinstanceof(self, html):
        return "Q11424"

    def findcast(self, html):
        return self.findallbyre('(?s)"/darsteller/[^"]*">(.*?)<', html, 'actor')

    def findpubdate(self, html):
        return self.findbyre('<h1>[^<>]*<small>\(([^<>]*)\)', html)


class TrackFieldAnalyzer(Analyzer):
    def setup(self):
        self.dbid = 'Q29384941'
        self.dbname = 'Track and Field Statistics'
        self.hrtre = '(<table align=center.*?</table>)'
        self.language = 'en'

    def findnames(self, html):
        return [self.findbyre('valign=top><b>(.*?)</b>', html)]

    def findlongtext(self, html):
        return self.findbyre('(?s)(<table align=center.*</table>)', html)

    def instanceof (self, html):
        return 'Q5'
    
    def findoccupations(self, html):
        return ['Q11513337']

    def findsports(self, html):
        return ['Q542']

    def findbirthdate(self, html):
        return self.findbyre('Born:(.*?)<', html)

    def findnationality(self, html):
        section = self.findbyre('(?s)(<table align=center.*?</table>)', html)
        return self.findbyre('.*valign=top><b>(.*?)<', section, 'country')
    

class TrackFieldFemaleAnalyzer(TrackFieldAnalyzer):
    def setup(self):
        TrackFieldAnalyzer.setup(self)
        self.dbproperty = 'P3924'
        self.urlbase = 'http://trackfield.brinkster.net/Profile.asp?ID={id}&Gender=W'

    def findgender(self, html):
        return 'Q6581072'


class TrackFieldMaleAnalyzer(TrackFieldAnalyzer):
    def setup(self):
        TrackFieldAnalyzer.setup(self)
        self.dbproperty = 'P3925'
        self.urlbase = 'http://trackfield.brinkster.net/Profile.asp?ID={id}&Gender=M'

    def findgender(self, html):
        return 'Q6581097'


class WhosWhoFranceAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P4124"
        self.dbid = 'Q5924723'
        self.dbname = "Who's Who in France"
        self.urlbase = 'https://www.whoswho.fr/bio/{id}'
        self.hrtre = '(<h1.*?<!-- profils proches -->)'
        self.language = 'fr'

    def findnames(self, html):
        return [
            self.findbyre('(?s)<h1[^<>]*>(.*?)<', html),
            self.findbyre('(?s)>Nom<.*?<div[^<>]*>(.*?)<', html)
            ]

    def finddescription(self, html):
        return self.findbyre('(?s)"jobTitle">(.*?)<', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)(<h1.*)<h2', html)

    def findinstanceof(self, html):
        return 'Q5'

    def findoccupations(self, html):
        section = self.findbyre('(?s)"jobTitle">(.*?)<', html)
        if section:
            return [self.getdata('occupation', part) for part in section.split(',')]

    def findbirthplace(self, html):
        return self.findbyre('(?s)>Ville de naissance<.*?<div[^<>]*>(.*?)<', html, 'city')

    def findnationality(self, html):
        return self.findbyre('(?s)>Pays de naissance<.*?<div[^<>]*>(.*?)<', html, 'country')

    def findtwitter(self, html):
        return self.findbyre('"https://twitter.com/([^<>"])"[^<>]*>[^<>]*sur Twitter<', html)
        

class AthenaeumAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P4145'
        self.dbid = 'Q32061534'
        self.dbname = 'Athenaeum'
        self.urlbase = 'http://www.the-athenaeum.org/people/detail.php?id={id}'
        self.hrtre = '(<div id="bio".*</table>'
        self.language = 'en'

    def finddescription(self, html):
        return self.findbyre('(?s)<td align="left">(?:\s|<[<>]*>)*([^<>\.]*)', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)<td align="left">(.*?)</td>', html)

    def findnames(self, html):
        return self.findallbyre('<strong>Name:</strong></td><td>(.*?)<', html)

    def findbirthdate(self, html):
        return self.findbyre('<strong>Dates:</strong></td><td>(.*?)[-<]', html)

    def finddeathdate(self, html):
        return self.findbyre('<strong>Dates:</strong></td><td>[^<>]*-(.*?)<', html)

    def findnationality(self, html):
        return self.findbyre('<strong>Nationality:</strong></td><td>(.*?)<', html, 'country')

    def findgender(self, html):
        return self.findbyre('<strong>Sex:</strong></td><td>(.*?)<', html, 'gender')

    def findincollections(self, html):
        section = self.findbyre('(?s)Top owners of works by this artist(.*?)</table>', html)
        if section:
            return self.findallbyre('<tr><td[^<>]*>(.*?)<', section, 'museum')


class FoihAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P4206'
        self.dbid = None
        self.dbname = 'FOIH'
        self.urlbase = 'https://inventaris.onroerenderfgoed.be/dibe/persoon/{id}'
        self.hrtre = '<!-- persoon velden -->(.*?)<!-- einde persoon velden -->'
        self.language = 'nl'

    def findinstanceof(self, html):
        return 'Q5'

    def findnames(self, html):
        return self.findallbyre('title" content="(.*?)"', html) +\
               self.findallbyre('<title>([^<>\|]+)', html) +\
               self.findallbyre('(?s)<h1>(.*?)<', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)<h3>Beschrijving</h3>(.*?)<h', html)
    
    def findbirthdate(self, html):
        return self.findbyre('(?s)<dd>Geboortedatum</dd>\s*<dt>(.*?)</dt>', html)

    def findbirthplace(self, html):
        return self.findbyre('(?s)<dd>Geboorteplaats</dd>\s*<dt>(.*?)</dt>', html, 'city')

    def finddeathdate(self, html):
        return self.findbyre('(?s)<dd>Sterfdatum</dd>\s*<dt>(.*?)</dt>', html)

    def finddeathplace(self, html):
        return self.findbyre('(?s)<dd>Plaats van overlijden</dd>\s*<dt>(.*?)</dt>', html, 'city')

    def findoccupations(self, html):
        section = self.findbyre('(?s)<dd>Beroep[^<>]*</dd>\s*<dt>(.*?)</dt>', html)
        if section:
            return self.findallbyre('([\w\s]+)', section, 'occupation')


class EoasAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P4228'
        self.dbid = 'Q19160682'
        self.dbname = 'Encyclopedia of Australian Science'
        self.urlbase = 'http://www.eoas.info/biogs/{id}'
        self.hrtre = '(?s)<div id="main">(.*?)<div'
        self.language = 'en'

    def isperson(self, html):
        return self.findinstanceof(html) == 'Q5'

    def findnames(self, html):
        result = [
            self.findbyre('<title>(.*?)(?: - |<)', html),
            self.findbyre('(?s)>([^<>]*)</h1>', html),
            self.findbyre('(?s)>([^<>]*)\([^<>]*</h1>', html),
            ]
        section = self.findbyre('(?s)<ul class="entitynames">(.*?)</ul>', html)
        if section:
            result += self.findallbyre('(?s)<li>(.*?)<', section)
        return result

    def findlongtext(self, html):
        return self.findbyre('(?s)<h3>Summary</h3>(.*?)</div>', html)

    def findinstanceof(self, html):
        return self.findbyre('(?s)<h1>\s*<span>(.*?)<', html, 'instanceof')

    def findbirthdate(self, html):
        if self.isperson(html):
            return self.findbyre('<dd class="startdate">(.*?)<', html)

    def finddeathdate(self, html):
        if self.isperson(html):
            return self.findbyre('<dd class="enddate">(.*?)<', html)

    def findbirthplace(self, html):
        if self.isperson(html):
            return self.findbyre('<dd class="startdate">[^<>]*<br\s*/>(.*?)<', html, 'city')
        
    def finddeathplace(self, html):
        if self.isperson(html):
            return self.findbyre('<dd class="enddate">[^<>]*<br\s*/>(.*?)<', html, 'city')
        
    def findoccupations(self, html):
        if self.isperson(html):
            sections = self.findallbyre('<dd class="function">(.*?)<', html)
            occupations = []
            for section in sections:
                occupations += section.split(' and ')
            result = []
            for occupation in occupations:
                result += self.findallbyre('([\w\s]+)', occupation, 'occupation')
            return result

    def findschools(self, html):
        if self.isperson(html):
            return self.findallbyre('Education - [^<>]* at (?:the )?(.*?)<', html, 'university')

    def finddegrees(self, html):
        if self.isperson(html):
            return self.findallbyre('Education - ([^<>]*?)(?:\(| at )', html, 'degree')

    def findemployers(self, html):
        if self.isperson(html):
            return self.findallbyre('Career position - [^<>]* at (?:the )?(.*?)<', html, 'employer', alt=['university'])

    def findwebsite(self, html):
        section = self.findbyre('<dd class="url">(.*?)</dd>', html)
        if section:
            return self.findbyre('href="(.*?)"', section)


class ItauAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P4399'
        self.dbid = 'Q41599984'
        self.dbname = 'Enciclopédia Itaú Cultural'
        if self.isperson:
            self.urlbase = 'https://enciclopedia.itaucultural.org.br/{id}'
        else:
            self.urlbase = None # Analyzer only created for persons, for works and possible other it can be extended later
        self.hrtre = '<h1[^<>]*>\s*Outras informações.*?<div class="section_content">(.*?)</section>'
        self.language = 'pt'
        self.htmlescape = True

    @property
    def isperson(self):
        return self.id.startswith('pessoa')

    def findinstanceof(self, html):
        if self.isperson:
            return 'Q5'

    def findnames(self, html):
        section = self.findbyre('(?s)Outros nomes.*?<ul>(.*?)</ul>', html)
        if section:
            result = self.findallbyre('(?s)>(.*?)<', section)
        else:
            result = []
        return result +\
               self.findallbyre('title" content="(.*?)[\|"]', html) +\
               self.findallbyre('(?s)<title>(.*?)[\|"]', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)<h2[^<>]*>\s*Biografia\s*</h2>(.*?)<h\d', html)

    def findoccupations(self, html):
        section = self.findbyre('(?s)>\s*Habilidades\s*<.*?<ul>(.*?)</ul>', html)
        if section:
            return self.findallbyre('(?s)>(.*?)<', section, 'occupation')

    def findchildren(self, html):
        return self.findallbyre('(?s)mãe de\s*<.*?>(.*?)<', html, 'person')

    def findbirthdate(self, html):
        return self.findbyre('(?s)>Data de nascimento[^<>]*</span>(.*?)<', html)

    def findbirthplace(self, html):
        return self.findbyre('(?s)>Local de nascimento[^<>]*</span>(.*?)<', html, 'city')

    def finddeathdate(self, html):
        return self.findbyre('(?s)>Data de morte[^<>]*</span>(.*?)<', html)

    def finddeathplace(self, html):
        return self.findbyre('(?s)>Local de morte[^<>]*</span>(.*?)<', html, 'city')

    


class SpanishBiographyAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P4459"
        self.dbid = "Q41705771"
        self.dbname = "Spanish Biographical Dictionary"
        self.urlbase = 'http://dbe.rah.es/biografias/{id}'
        self.hrtre = '(<div class="field--item">.*?</article>)'
        self.language = 'es'

    def finddescription(self, html):
        return self.findbyre('(?:<span style="font-family:\'Times New Roman\';">|</b>)\.?(.*?)<', html)

    def findnames(self, html):
        return [self.findbyre('"twitter:title" content="(.*?)"', html)]

    def findlongtext(self, html):
        return self.findbyre('(?s)<div class="field--label[^<>]*">Biograf.a</div>(.*?)</div>', html)

    def findinstanceof(self, html):
        return "Q5"

    def findbirthdate(self, html):
        return self.findbyre('"description" content="[^"]+\(([^"]*?)–', html) or\
               self.findbyre('(?:<span style="font-family:\'Times New Roman\';">|</b>)[^<>]*?((?:\d+\.\w+\.)?\d+) –', html)

    def finddeathdate(self, html):
        return self.findbyre('"description" content="[^"]+–([^"]*?)\)', html) or\
               self.findbyre('(?:<span style="font-family:\'Times New Roman\';">|</b>)[^<>]*? – [^<>]*?((?:\d+\.\w+\.)?\d+)', html)

    def findbirthplace(self, html):
        return self.findbyre('(?:<span style="font-family:\'Times New Roman\';">|</b>)\.?([^<>–,]*),', html, 'city')

    def finddeathplace(self, html):
        return self.findbyre('(?:<span style="font-family:\'Times New Roman\';">|</b>)[^<>]*?– ([^<>]*?),', html, 'city')

    def findoccupations(self, html):
        section = self.findbyre('(?:<span style="font-family:\'Times New Roman\';">|</b>)[^<>]+\.([^<>]+)', html)
        if section:
            return self.findallbyre('([\s\w]+)', section, 'occupation')


class CommonwealthGamesAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P4548'
        self.dbid = None
        self.dbname = 'Commonwealth Games Federation'
        self.urlbase = 'https://thecgf.com/results/athletes/{id}'
        self.hrtre = '(<h2 class="table-title">.*?)</section>'
        self.language = 'en'

    def findnames(self, html):
        return self.findallbyre('name" content="(.*?)"', html) +\
               self.findallbyre('<title>(.*?)[\|<]', html) +\
               self.findallbyre('<h\d[^<>]*>(.*?)<', html)

    def findinstanceof(self, html):
        return 'Q5'

    def findnationalities(self, html):
        return self.findallbyre('"Country"><[^<>]*>(.*?)<', html, 'country')

    def findparticipations(self, html):
        return self.findallbyre('"Games"><[^<>]*>(.*?)<', html, 'commonwealth-games')

    def findsports(self, html):
        return self.findallbyre('"Event"><[^<>]*>([^<>]*?)-', html, 'sport')

    def findgender(self, html):
        return self.findbyre('"Event"><[^<>]*>[^<>]*-(.*?)<', html, 'gender')


class OnlineBooksAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P4629"
        self.dbid = None
        self.dbname = "Online Books Page"
        self.urlbase = "http://onlinebooks.library.upenn.edu/webbin/book/lookupname?key={id}"
        self.hrtre = '(<h2 .*?/h3>)'
        self.language = 'en'

    def finddescription(self, html):
        return self.findbyre('<title>(.*?)[\|<]', html)

    def findnames(self, html):
        return [self.findbyre('<title>(.*?)[\(\|<]', html)]

    def findfirstname(self, html):
        return self.findbyre('<h3[^<>]*>[^<>]*\([^<>,]*?,\s*(\w+)', html, 'firstname')

    def findlastname(self, html):
        return self.findbyre('<h3[^<>]*>[^<>]*\(([^<>,]*?),', html, 'lastname')

    def findbirthdate(self, html):
        return self.findbyre('<h3[^<>]*>[^<>]*\([^<>]*,([^<>]*)-', html)

    def finddeathdate(self, html):
        return self.findbyre('<h3[^<>]*>[^<>]*\([^<>]*,[^<>]*-([^<>]*)\)', html)


class NumbersAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P4657'
        self.dbid = 'Q17072251'
        self.dbname = 'The Numbers'
        self.urlbase = 'https://www.the-numbers.com/person/{id}'
        #self.urlbase = None # temporarily?
        self.language = 'en'

    def findnames(self, html):
        return [self.findbyre('<h1.*?>(.*?)<', html)]

    def findoccupations(self, html):
        return self.findallbyre('"jobTitle">(.*?)<', html, 'occupation')


class DacsAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P4663'
        self.dbid = None
        self.dbname = 'DACS'
        self.urlbase = 'https://www.dacs.org.uk/licensing-works/artist-search/artist-details?ArtistId={id}'
        self.hrtre = '(<h1.*?)<h2'
        self.language = 'en'

    def findlongtext(self, html):
        return self.findbyre('(?s)(<h1.*?)<h2', html)
        
    def findnationalities(self, html):
        return self.findallbyre('lbNationality">(.*?)<', html, 'country')

    def findfirstname(self, html):
        return self.findbyre('lbFirstName\d*">(.*?)<', html, 'firstname')

    def findlastname(self, html):
        return self.findbyre('lbLastName\d*">(.*?)(?:,\s*)?<', html, 'lastname')

    def findbirthdate(self, html):
        return self.findbyre('lblDate[oO]fBirth">(.*?)<', html)

    def finddeathdate(self, html):
        return self.findbyre('lblDate[oO]fDeath">-*(.*?)<', html)


class CinemagiaAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P4666'
        self.dbid = 'Q15065727'
        self.dbname = 'CineMagia'
        self.urlbase = 'https://www.cinemagia.ro/actori/{id}/'
        #self.urlbase = None
        self.hrtre = '(<div class="detalii.block info.actor">.*?after.actor.biography -->)'
        self.language = 'ro'

    def findnames(self, html):
        return [self.findbyre('"og:title"[^<>]*content="(.*?)"', html)]

    def finddescription(self, html):
        return self.findbyre('"description"[^<>]*content="(.*?)"', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)(<div class="detalii.block info.actor">.*?after.actor.biography -->)', html)

    def findbirthplace(self, html):
        return self.findbyre('(?s)<b>Locul naşterii</b>:([^<>]*)', html, 'city')

    def findbirthdate(self, html):
        return self.findbyre('(?s)<b>Data naşterii</b>.*?>([^<>]*)</a>', html)

    def findoccupations(self, html):
        section = self.findbyre('(?s)<b>Ocupaţie</b>:([^<>]*)', html)
        if section:
            return self.findbyre('([\w\s]+)', section, 'occupation')


class PeintresBelgesAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P4687"
        self.dbid = None
        self.dbname = "Dictionnaire des peintres belges"
        self.urlbase = "http://balat.kikirpa.be/peintres/Detail_notice.php?id={id}"
        self.urlbase3 = "http://balat.kikirpa.be/peintres/Detail_notice_comp.php?id={id}"
        self.hrtre = '(<h4.*?)<span class="moyen"'
        self.language = 'fr'
        self.escapeunicode = True

    def finddescription(self, html):
        return self.findbyre('<span class="moyen">([^<>]*?)\.', html)

    def findnames(self, html):
        return [self.findbyre('<h4>(.*?)<', html)]

    def findlongtext(self, html):
        return self.findbyre('<span class="moyen">(.*?)</span>', html)

    def findbirthplace(self, html):
        return self.findbyre('"flash">([^<>]*?),', html, 'city')

    def findbirthdate(self, html):
        return self.findbyre('"flash">(?:[^<>]*,)?([^<>,\-]*?)[<-]', html)

    def finddeathplace(self, html):
        return self.findbyre('"flash">[^<>]*? - ([^<>]*?),', html, 'city')

    def finddeathdate(self, html):
        return self.findbyre('"flash">[^<>]*? - (?:[^<>]*,)?([^<>,\-])*<', html)

    def findincollections(self, html):
        section = self.findbyre('(?s)Collections</span>(.*?)</table>', html)
        if section:
            return self.findallbyre('<span[^<>]*>(.*?)<', section, 'museum')


class AuteursLuxembourgAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P4749"
        self.dbid = "Q47341245"
        self.dbname = "Dictionnaire des auteurs luxembourgeois"
        self.urlbase = "http://www.autorenlexikon.lu/page/author/{id}/DEU/index.html"
        self.hrtre = '(<h1.*<div style="clear:both">)'
        self.language = 'fr'

    def finddescription(self, html):
        return self.findbyre('itemprop="description">(.*?)</p>', html)

    def findnames(self, html):
        return self.findallbyre('itemprop="[^<>"]*[nN]ame">(.*?)<', html)

    def findlongtext(self, html):
        return self.findbyre('itemprop="description">(.*?)</div>', html)

    def findbirthdate(self, html):
        return self.findbyre('itemprop="birthDate" datetime="(.*?)"', html)

    def findbirthplace(self, html):
        return self.findbyre('itemprop="birthPlace".*?>(.*?)[\(<]', html, 'city')

    def finddeathdate(self, html):
        return self.findbyre('itemprop="deathDate" datetime="(.*?)"', html)

    def finddeathplace(self, html):
        return self.findbyre('itemprop="deathPlace".*?>(.*?)[<\(]', html, 'city')


class LuminousAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P4759'
        self.dbid = 'Q6703301'
        self.dbname = "Luminous-Lint"
        self.urlbase = "http://www.luminous-lint.com/app/photographer/{id}"
        self.hrtre = '<table cellpadding="5" cellspacing="0" border="0" bgcolor="#E0E0E0" width="100%">(.*?)</table>&nbsp;'
        self.language = 'en'

    def findnames(self, html):
        section = self.findbyre('<td[^<>]*>Names:</td>(?:<[^<>]*>)*<td>(.*?)</td>', html)
        if section:
            return self.findallbyre(';(.+?)&', section)

    def findlongtext(self, html):
        return (self.findbyre('(?s)<table cellpadding="5" cellspacing="0" border="0" bgcolor="#E0E0E0" width="100%">(.*?)<h1>', html) or '').replace('&nbsp;', ' ')

    def findbirthdate(self, html):
        return self.findbyre('Dates:\s*</td><td[^<>]*>(.*?)[\-<]', html.replace('&nbsp;', ' '))
    
    def finddeathdate(self, html):
        return self.findbyre('Dates:\s*</td><td[^<>]*>[^\-]+-([^\-<]+)<', html.replace('&nbsp;', ' '))

    def findbirthplace(self, html):
        return self.findbyre('Born:\s*</td><td[^<>]*>(.*?)<', html.replace('&nbsp;', ' '), 'city')

    def findworkplaces(self, html):
        return [self.findbyre('Active:\s*</td><td[^<>]*>(.*?)<', html.replace('&nbsp;', ' '), 'city')]

    def finddeathplace(self, html):
        return self.findbyre('Died:\s*</td><td[^<>]*>(.*?)<', html.replace('&nbsp;', ' '), 'city')

    
class AmericanBiographyAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P4823"
        self.dbid = "Q465854"
        self.dbname = "American National Biography"
        self.urlbase = "http://www.anb.org/view/10.1093/anb/9780198606697.001.0001/anb-9780198606697-e-{id}"
        self.hrtre = '(<h1.*?)<div class="contentRestrictedMessage">'
        self.language = 'en'

    def finddescription(self, html):
        return self.findbyre('(?s)<h3>Extract</h3>(.*?)</p>', html)

    def findnames(self, html):
        return [self.findbyre('"pf:contentName" : "([^"]*)\(', html)]

    def findlongtext(self, html):
        return self.findbyre('(?s)<p class="ency">(.*?)<div class="chunkFoot">', html)

    def findinstanceof(self, html):
        return "Q5"

    def findbirthdate(self, html):
        return self.findbyre('(<span class="date">([^<>]*)–', html)

    def finddeathdate(self, html):
        return self.findbyre('(<span class="date">[^<>]*–([^<>]+)', html)

    def findoccupations(self, html):
        section = re.compile('\)([^<>]*)was born', html)
        if section:
            return self.findallbyre('([\w\s]+)', section, 'occupation')

    def findbirthplace(self, html):
        return self.findbyre('was born \w+ ([\w\s]+)', html, 'city')

    def findfirstname(self, html):
        return self.findbyre('<span class="name">[^<>]*,([^<>]*)', html, 'firstname')

    def findlastname(self, html):
        return self.findbyre('<span class="name">([^<>]*),', html, 'lastname')


class GeprisAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P4872'
        self.dbid = 'Q48879895'
        self.dbname = 'GEPRIS'
        self.urlbase = 'http://gepris.dfg.de/gepris/person/{id}'
        self.urlbase = None # redirect complaints
        self.hrtre = '(<h3.*?)<div class="clear">'
        self.language = 'en'

    def finddescription(self, html):
        return self.findbyre('(?s)name="description"[^<>]*content="([^<>]*?)"', html)

    def findinstanceof(self, html):
        return "Q5"

    def findemployers(self, html):
        return [self.findbyre('(?s)>Adresse</span>\s*<span[^<>]*>(.*?)<', html, 'university', alt=['employer'])]

    def findwebsite(self, html):
        return self.findbyre('(?s)Internet<.*?<a[^<>]+class="extern"[^<>]+href="([^<>]*?)"', html)

    def findgender(self, html):
        if "Antragstellerin<" in html:
            return 'Q6581072'
        elif "Antragsteller<" in html:
            return 'Q6581097'

    def findresidences(self, html):
        return self.findbyre('(?s)Adresse</span>.*?>([^<>]*)(?:<[^<>]*>|\s)*</span>', html, 'city')


class WebumeniaAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P4887'
        self.dbid = 'Q50828580'
        self.dbname = 'Web umenia'
        self.urlbase = 'https://www.webumenia.sk/autor/{id}'
        self.hrtre = '<div class="col-sm-8 popis">(.*?)<div class="container-fluid'
        self.language = 'sk'
        self.escapehtml = True
        
    def findnames(self, html):
        return self.findallbyre('itemprop="name">(.*?)<', html)

    def findbirthdate(self, html):
        return self.findbyre('itemprop="birthDate">(.*?)<', html)

    def findbirthplace(self, html):
        return self.findbyre('itemprop="birthPlace">(.*?)<', html, 'city')

    def finddeathdate(self, html):
        return self.findbyre('itemprop="deathDate">(.*?)<', html)

    def finddeathplace(self, html):
        return self.findbyre('itemprop="deathPlace">(.*?)<', html, 'city')

    def findoccupations(self, html):
        return self.findallbyre('itemprop="jobTitle">(.*?)<', html, 'occupation')

    def findworkplaces(self, html):
        section = self.findbyre('(?s)Pôsobenie</h4>(.*?)</div>', html)
        if section:
            return self.findallbyre('\?place=([^"<>]*)">', section, 'city')

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html, includesocial=False)

    def findwebpages(self, html):
        section = self.findbyre('(?s)Externé odkazy</h4>(.*?)</div>', html)
        if section:
            return self.findallbyre('href="([^"]*)" target="_blank"', section)


class InvaluableAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P4927'
        self.dbid = None
        self.dbname = 'Invaluable.com'
        self.urlbase = 'https://www.invaluable.com/artist/-{id}'
        self.hrtre = '(\{"artist".*?\})'
        self.language = 'en'

    def findnames(self, html):
        f = open('result.html', 'w')
        f.write(html)
        f.close()
        section = self.findbyre('"alias":\[(.*?)\]', html)
        if section:
            return self.findallbyre('"(.*?)"', section) + [self.findbyre('"displayName":"(.*?)"', html)]
        else:
            return [self.findbyre('"displayName":"(.*?)"', html)]

    def findoccupations(self, html):
        section = self.findbyre('"profession":\[(.*?)\]', html)
        if section:
            return self.findallbyre('"(.*?)"', html, 'occupation')

    def findbirthdate(self, html):
        return self.findbyre('"dates":"(.*?)[\-"]', html)

    def finddeathdate(self, html):
        return self.findbyre('"data":"[^"]*-(.*?)"', html)

    def findfirstname(self, html):
        return self.findbyre('"foreName":"(.*?)"', html)

    def findlastname(self, html):
        return self.findbyre('"lastName":"(.*?)"', html)


class AinmAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P4929'
        self.dbid = None
        self.dbname = 'AINM'
        self.urlbase = 'https://www.ainm.ie/Bio.aspx?ID={id}'
        self.hrtre = '<div id="sidebar" .*?>(.*?)<!-- #sidebar-->'
        self.language = 'ga'

    def getvalue(self, field, html, category=None):
        return self.findbyre('(?s)<td class="caption">%s</td>\s*<td class="value">(.*?)</td>'%field, html, category)

    def findlongtext(self, html):
        return self.findbyre('(?s)<div class="article">(.*?)<div id="machines"', html)
    
    def findinstanceof(self, html):
        return 'Q5'

    def findnames(self, html):
        result = [self.findbyre('<meta name="title" content="(.*?)[\(\|"]', html)]
        section = self.getvalue('ainm eile', html)
        if section:
            return result + self.findallbyre('>([^<>]+)</', section)
        else:
            return result

    def findbirthdate(self, html):
        return self.getvalue('dáta breithe', html) or\
               self.findbyre('"article-title">(?:<[^<>]*>)*[^<>]*\(<[^<>]*>(\d+)</a>-', html)

    def finddeathdate(self, html):
        return self.getvalue('dáta báis', html) or\
               self.findbyre('"article-title">(?:<[^<>]*>)*[^<>]*\(.*?-<[^<>]*>(\d+)</a>', html)

    def findbirthplace(self, html):
        section = self.getvalue('áit bhreithe', html)
        if section:
            return self.findbyre('>([^<>]+)</', section, 'city')

    def findgender(self, html):
        return self.getvalue('inscne', html, 'gender')

    def findschools(self, html):
        return [self.getvalue('scoil', html, 'university')]

    def findoccupations(self, html):
        section = self.getvalue('slí bheatha', html)
        if section:
            return self.findallbyre('>([^<>]*)</a>', section, 'occupation')


class TmdbAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P4985'
        self.dbid = 'Q20828898'
        self.dbname = 'The Movie Database'
        self.urlbase = 'https://www.themoviedb.org/person/{id}'
        self.hrtre = '(<div id="left_column".*?)</section>'
        self.language = 'en'

    def getvalue(self, field, html, dtype=None, alt=[]):
        return self.findbyre('(?s)<bdi>%s</bdi></strong>(.*?)</p>'%field, html, dtype, alt=alt)

    def findnames(self, html):
        return self.findallbyre('title" content="(.*?)"', html) +\
               self.findallbyre('<h2>(.*?)</', html) +\
               self.findallbyre('itemprop="[^"]*[nN]ame">(.*?)<', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)<h3 dir="auto">Biography</h3>.*?<div class="text">(.*?)</div>', html)

    def finddescription(self, html):
        longtext = self.findlongtext(html)
        if longtext:
            return longtext.split('.')[0]

    def findoccupations(self, html):
        return [self.getvalue('Known For', html, 'film-occupation', alt=['occupation'])]

    def findgender(self, html):
        return self.getvalue('Gender', html, 'gender')

    def findbirthdate(self, html):
        return self.getvalue('Birthday', html)

    def finddeathdate(self, html):
        return self.getvalue('Day of Death', html)

    def findbirthplace(self, html):
        return self.getvalue('Place of Birth', html, 'city')

    def findwebsite(self, html):
        site = self.getvalue('Official Site', html)
        if site and ':' in site:
            return site

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html[:html.find('<footer')])


class LibraryKoreaAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P5034'
        self.dbid = 'Q56640487'
        self.dbname = 'National Library of Korea'
        self.urlbase = 'https://nl.go.kr/authorities/resource/{id}'
        self.hrtre = '<div class="kac_number_area">(.*?)</tbody>'
        self.language = 'ko'

    def getvalue(self, field, html, dtype=None):
        return self.findbyre('(?s)<td id="%s" title="([^"<>]+)">', html, dtype)

    def getvalues(self, field, html, dtype=None):
        section = self.getvalue(field, html)
        if section:
            return self.findallbyre('([^;]*)', section, dtype)

    def findnames(self, html):
        return self.getvalues("other_name", html)

    def findbirthdate(self, html):
        section = self.getvalue("birth_year", html)
        if section:
            return self.findbyre('(.*)-', section)

    def finddeathdate(self, html):
        section = self.getvalue("birth_year", html)
        if section:
            return self.findbyre('-(.*)', section)

    def findnationalities(self, html):
        return self.getvalues("nationality", html, 'country')

    def findoccupations(self, html):
        return self.getvalues("job", html, 'occupation')

    def findlanguagesspoken(self, html):
        return self.getvalues("f_language", html, 'language')

    def findworkfields(self, html):
        return self.getvalues("field_of_activity", html, 'subject')

    def findemployers(self, html):
        descriptions = self.getvalues("relsated_org")
        return [self.findbyre('([^\(\)]+)', desc, 'employer') for desc in descriptions]

    def findmixedrefs(self, html):
        return self.defaultmixedrefs(html)


class KunstenpuntAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P5068"
        self.dbid = None
        self.dbname = "Kunstenpunt"
        self.urlbase = 'http://data.kunsten.be/people/{id}'
        self.hrtre = '(<h3>Details.*?)<h3'
        self.language = 'nl'

    def getvalue(self, field, html, category=None):
        return self.findbyre('<dt>%s</dt><dd>(.*?)<'%field, html, category)

    def findnames(self, html):
        return [self.getvalue('Volledige naam', html)]

    def finddescription(self, html):
        return self.getvalue('Sleutelnaam', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)(<h3>Details.*?)<h3', html)

    def findbirthdate(self, html):
        return self.getvalue('Geboren', html)

    def findgender(self, html):
        return self.getvalue('Geslacht', html, 'gender')

    def findlastname(self, html):
        return self.getvalue('Naam', html, 'lastname')

    def findfirstname(self, html):
        return self.getvalue('Voornaam', html, 'firstname')

    def findnationality(self, html):
        return self.getvalue('Land', html, 'country')


class ArtistsCanadaAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P5239"
        self.dbid = None
        self.dbname = "Artists in Canada"
        self.urlbase = 'https://app.pch.gc.ca/application/aac-aic/artiste_detailler_bas-artist_detail_bas.app?lang=en&rID={id}'
        self.hrtre = '(<section class="maincontentpart">.*?</section>)'
        self.language = 'en'

    def findinstanceof(self, html):
        return "Q5"

    def findnames(self, html):
        result = [self.findbyre('(?s)<dt>Artist/Maker.*?<dd>(.*?)</dd>', html)]
        section = self.findbyre('(?s)<dt>Artist other names.*?<dd>(.*?)</dd>', html)
        if section:
            result += self.findallbyre('(?s)<li>(.*?)<', html)
        return result

    def findfirstname(self, html):
        return self.findbyre('(?s)Artist/Maker\s*</dt>\s*<dd[^<>]*>[^<>]*,\s*(\w+)', html, 'firstname')

    def findlastname(self, html):
        return self.findbyre('(?s)Artist/Maker\s*</dt>\s*<dd[^<>]*>([^<>]*?),', html, 'lastname')

    def findoccupations(self, html):
        section = self.findbyre('(?s)Technique\s*</dt>.*?<dd[^<>]*>(.*?)</dd>', html)
        if section:
            return self.findallbyre('(?s)>(.*?)<', section, 'occupation')

    def findgender(self, html):
        return self.findbyre('(?s)<dt>Gender.*?<dd[^<>]*>(.*?)</dd>', html, 'gender')

    def findbirthplace(self, html):
        section = self.findbyre('(?s)<dt>Birth.*?<dd[^<>]*>(.*?)</dd>', html)
        if section:
            return self.findbyre('(?s)>([^,<>]*),[^<>]*</li>', section, 'city') or\
                   self.findbyre('(?s)>([^,<>]*)</li>', section, 'city')

    def findbirthdate(self, html):
        section = self.findbyre('(?s)<dt>Birth.*?<dd[^<>]*>(.*?)</dd>', html)
        if section:
            return self.findbyre('(?s)<time>(.*?)</time>', section)

    def finddeathplace(self, html):
        section = self.findbyre('(?s)<dt>Death.*?<dd[^<>]*>(.*?)</dd>', html)
        if section:
            return self.findbyre('(?s)>([^,<>]*),[^<>]*</li>', section, 'city') or\
                   self.findbyre('(?s)>([^,<>]*)</li>', section, 'city')

    def finddeathdate(self, html):
        section = self.findbyre('(?s)<dt>Death.*?<dd[^<>]*>(.*?)</dd>', html)
        if section:
            return self.findbyre('(?s)<time>(.*?)</time>', section)

    def findresidences(self, html):
        section = self.findbyre('(?s)(<dt>Address.*?<dd[^<>]*>.*?</dd>)', html)
        if section:
            result = self.findbyre('(?s)>([^,<>]*),[^<>]*</li>', section, 'city') or\
                     self.findbyre('(?s)>([^,<>]*)</li>', section, 'city')
            return [result]

    def findnationality(self, html):
        return self.findbyre('(?s)<dt>Citizenship.*?<dd[^<>]*>(.*?)</dd>', html, 'country')


class PornhubAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P5246'
        self.dbid = 'Q936394'
        self.dbname = 'Pornhub'
        self.urlbase = 'https://nl.pornhub.com/pornstar/{id}'
        self.hrtre = '<div class="detailedInfo">(.*?)</section>'
        self.language = 'nl'
        self.showurl = False

    def findnames(self, html):
        return [self.findbyre('(?s)<h1>(.*?)<', html)]

    def findbirthdate(self, html):
        return self.findbyre('itemprop="birthDate"[^<>]*>(.*?)<', html) or\
               self.findbyre('(?s)<span>Geboren:</span>(.*?)<', html)

    def findbirthplace(self, html):
        return self.findbyre('itemprop="birthPlace"[^<>]*>(.*?)<', html, 'city') or\
               self.findbyre('(?s)<span>Geboorteplaats:</span>(.*?)<', html, 'city')

    def finddeathdate(self, html):
        return self.findbyre('itemprop="deathDate"[^<>]*>(.*?)<', html)

    def finddeathplace(self, html):
        return self.findbyre('itemprop="deathPlace"[^<>]*>(.*?)<', html, 'city')

    def findheight(self, html):
        return self.findbyre('itemprop="height"[^<>]*>[^<>]*\(([^<>]*)\)', html) or\
               self.findbyre('(?s)<span>Lengte:</span>[^<>]*\(([^<>]*\)', html)

    def findweights(self, html):
        return [
            self.findbyre('itemprop="weight"[^<>]*>([^<>]*)\(', html),
            self.findbyre('itemprop="weight"[^<>]*>[^<>]*\(([^<>]*)\)', html),
            self.findbyre('(?s)<span>Gewicht:</span>[^<>]*\(([^<>]*)\)', html),
            self.findbyre('(?s)<span>Gewicht:</span>([^<>]*?)\(', html),
            ]

    def findwebsite(self, html):
        return self.findbyre('(?s)href="([^<>]*?)"[^<>]*>\s*Officiële Site', html)

    def findoccupations(self, html):
        return ['Q488111']


class YoupornAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P5267'
        self.dbid = None
        self.dbname = 'YouPorn'
        self.urlbase = 'https://www.youporn.com/pornstar/{id}/'
        self.hrtre = '<div class="porn-star-columns">(.*?)<div'
        self.language = 'en'
        self.showurl = False

    def findinstanceof(self, html):
        return 'Q5'

    def findnames(self, html):
        section = self.findbyre('(?s)(<h1.*?<)/div>', html)
        if section:
            result = []
            subsections = self.findallbyre('(?s)>(.*?)<', section)
            for subsection in subsections:
                result += self.findallbyre('([^,]+)', subsection)
            return result

    def findbirthdate(self, html):
        return self.findbyre('<label>Born:</label><span>(.*?)<', html)

    def finddeathdate(self, html):
        return self.findbyre('<label>Died:</label><span>(.*?)<', html)

    def findheight(self, html):
        return self.findbyre('<label>Height:</label><span>[^<>]*?\((.*?)\)', html)

    def findweights(self, html):
        return [
            self.findbyre('<label>Weight:</label><span>([^<>]*?)\(', html),
            self.findbyre('<label>Weight:</label><span>[^<>]*?\((.*?)\)', html)
            ]

    def findethnicities(self, html):
        section = self.findbyre('<label>Ethnicity:</label>(.*?)</li>', html)
        if section:
            return self.findallbyre('>(.*?)<', section, 'ethnicity')
        
    def findhaircolor(self, html):
        return self.findbyre('<label>Hair:</label><span>(.*?)</span>', html, 'haircolor')

    def findoccupations(self, html):
        return ['Q488111']


class NelsonAtkinsAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P5273'
        self.dbid = None
        self.dbname = "Nelson-Atkins Museum"
        self.urlbase = 'https://art.nelson-atkins.org/people/{id}'
        self.hrtre = '(<h1>.*?)<div class="emuseum-detail-category'
        self.language = 'en'

    def findlongtext(self, html):
        return self.findbyre('(?s)(<h1>.*?)View All Works', html)

    def findnames(self, html):
        return [self.findbyre('<h1>(.*?)<', html)]

    def findinstanceof(self, html):
        return 'Q5'

    def findnationality(self, html):
        return self.findbyre('filter=nationality.3A([^<>]*)"', html, 'country')

    def findbirthdate(self, html):
        return self.findbyre('born ([^<>]*)</', html) or self.findbyre('<h3>[^<>]*,([^<>]*)-', html)

    def finddeathdate(self, html):
        return self.findbyre('<h3>[^<>]*,[^<>]*-([^<>]*)', html)

    def findbirthplace(self, html):
        return self.findbyre('<div class="detailField biographyField">born:(.*?)<', html, 'city')

    def findgender(self, html):
        if '"/vocabularies/thesaurus/1547188"' in html:
            return 'Q6581072'

    def findincollections(self, html):
        return ['Q1976985']


class ArmbAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P5329"
        self.dbid = None
        self.dbname = "ARMB"
        self.urlbase = 'http://www.armb.be/index.php?id={id}'
        self.hrtre = '<div id="before_content_block">(.*?)<!--  Text: \[end\] -->'
        self.language = 'fr'
        
    def findnames(self, html):
        return [self.findbyre('"DC.title"[^<>]*content="(.*?)"', html)]

    def finddescription(self, html):
        return self.findbyre('"DC.description"[^<>]*content="(.*?)"', html)

    def findlongtext(self, html):
        parts = self.findallbyre('(?s)<p class="bodytext">(.*?)</p>', html)
        if parts:
            return '\n'.join(parts)

    def findbirthplace(self, html):
        return self.findbyre('Née? à (.*?),? (?:\(|le )', html, 'city')

    def findbirthdate(self, html):
        return self.findbyre('Née?[^<>,]*(?:le|en)\s([^<>\.\(\)]*)', html)

    def finddeathplace(self, html):
        return self.findbyre('écédée? à (.*?),? (?:\(|le )', html, 'city')

    def finddeathdate(self, html):
        return self.findbyre('écédée?[^<>]*(?:le|en)\s([^<>\.\(\)]*)', html)

    def findassociations(self, html):
        return self.findallbyre('Professeur à (.*?)\.', html, 'university')

    def findworkfields(self, html):
        section = self.findbyre('Spécialités\s*:\s*([^<>]*)', html)
        if section:
            parts = section.split(' et ')
            result = []
            for part in parts:
                result += self.findallbyre('([^,;\-\.]*)', part, 'subject')
            return result
        else:
            return self.findallbyre('Spécialité\s*:\s*([^<>]*)', html, 'subject')

    def findmemberships(self, html):
        return ['Q2124852']


class OperoneAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P5359'
        self.dbid = 'Q55019828'
        self.dbname = 'Operone'
        self.urlbase = 'http://www.operone.de/komponist/{id}.html'
        self.hrtre = '<body>(.*?)<span class="vb">'
        self.language = 'de'
        self.escapehtml = True

    def findnames(self, html):
        result = self.findbyre('<b>(.*?)<br>', html)
        if result:
            return [self.TAGRE.sub('', result)]

    def finddescription(self, html):
        return self.findbyre('<br>([^<>]*)</p>', html)

    def findinstanceof(self, html):
        return 'Q5'

    def findbirthdate(self, html):
        return self.findbyre('\* (.*?)(?: in |<)', html)

    def findbirthplace(self, html):
        return self.findbyre('\* [^<>]* in (.*?)<', html, 'city')

    def finddeathdate(self, html):
        return self.findbyre('\+ (.*?)(?: in |<)', html)

    def finddeathplace(self, html):
        return self.findbyre('\+ [^<>]* in (.*?)<', html, 'city')

    def findoccupations(self, html):
        section = self.findbyre('<br>([^<>]*)</p>', html)
        if section:
            result = []
            subsections = section.split(' und ')
            for subsection in subsections:
                result += [self.getdata('occupation', text) for text in subsection.split(',')]
            return result


class BnbAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P5361"
        self.dbid = "Q919757"
        self.dbname = "British National Bibliography"
        self.urlbase = 'http://bnb.data.bl.uk/doc/person/{id}'
        self.hrtre = '(<table id="id.*?)</section>'
        self.language = 'en'

    def findnames(self, html):
        return [self.findbyre('(?s)<th class="label">name</th>.*?"value">(.*?)<', html)]

    def finddescription(self, html):
        return self.findbyre('<h1>(.*?)</', html)

    def findfirstname(self, html):
        return self.findbyre('(?s)<th class="label">given name</th>.*?"value">(.*?)<', html, 'firstname')

    def findinstanceof(self, html):
        section = self.findbyre('(?s)th class="label">type</th>(.*?)>/table>', html)
        if section:
            for result in self.findallbyre('>(.*?)</a>', section, 'instanceof'):
                if result:
                    return result

    def findlastname(self, html):
        return self.findbyre('(?s)<th class="label">family name</th>.*?"value">(.*?)<', html, 'lastname')

    def findbirthdate(self, html):
        return self.findbyre('/birth">(.*?)<', html)

    def finddeathdate(self, html):
        return self.findbyre('/death">(.*?)<', html)

    def findisni(self, html):
        return self.findbyre('"http://isni.org/isni/(.*?)"', html)

    def findviaf(self, html):
        return self.findbyre('"http://viaf.org/viaf/(.*?)"', html)


class InternetBookAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P5365'
        self.dbid = 'Q55071470'
        self.dbname = 'Internet Book Database'
        self.urlbase = 'http://www.ibdof.com/author_details.php?author={id}'
        self.hrtre = '<dl class="bio-details">(.*?)</dl>'
        self.language = 'en'

    def getvalue(self, field, html, dtype=None):
        return self.findbyre('<dt>%s:</dt><dd>(.*?)</dd>'%field, html, dtype)

    def findnames(self, html):
        return [self.getvalue('Full Name', html)]

    def findlongtext(self, html):
        return self.findbyre('(?s)<div class="col-right">(.*?)</div>', html)

    def findwebsite(self, html):
        section = self.getvalue('Website', html)
        if section:
            return self.findbyre('>([^<>]*)</a>', section)

    def findbirthplace(self, html):
        return self.getvalue('Birthplace', html, 'city')

    def findbirthdate(self, html):
        return self.getvalue('Birth date', html)

    def finddeathplace(self, html):
        return self.getvalue('Deathplace', html, 'city')

    def finddeathdate(self, html):
        return self.getvalue('Death date', html)

    def findresidences(self, html):
        return [self.getvalue('Place of Residence', html, 'city')]


class BiuSanteAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P5375'
        self.dbid = None
        self.dbname = 'Bibliothèque interuniversitaire de Santé'
        self.urlbase = 'http://www.biusante.parisdescartes.fr/histoire/biographies/index.php?cle={id}'
        self.hrtre = '<h2.*?(<h2.*?</table>)'
        self.language = 'fr'
        self.escapehtml = True

    def findnames(self, html):
        return self.findallbyre('(?s)<h2>(.*?)<', html)

    def finddescription(self, html):
        return self.findbyre('(?s)Détails biographiques<.*?<td[^<>]*>(.*?)\.?<', html)

    def findbirthdate(self, html):
        return self.findbyre('(?s)Naissance<.*?<td[^<>]*>\s*([\d/]+)', html)

    def findbirthplace(self, html):
        return self.findbyre('(?s)Naissance<.*?<td[^<>]*>[^<>]*?à(.*?)[\(<]', html, 'city')

    def finddeathdate(self, html):
        return self.findbyre('(?s)Décès<.*?<td[^<>]*>\s*([\d/]+)', html)

    def finddeathplace(self, html):
        return self.findbyre('(?s)Déces<.*?<td[^<>]*>[^<>]*?à(.*?)[\(<]', html, 'city')

    def findoccupations(self, html):
        section = self.findbyre('(?s)Détails biographiques<.*?<td[^<>]*>(.*?)\.?<', html)
        if section:
            return self.findallbyre('(\w{4,})', section, 'occupation')

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html, includesocial=False)


class PoetsWritersAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = "P5394"
        self.dbid = "Q7207541"
        self.dbname = "Poets & Writers"
        self.urlbase = 'https://www.pw.org/content/{id}'
        self.hrtre = '(<span property="schema:mainEntity">.*?</article>)'
        self.language = 'en'
        self.escapehtml = True

    def getvalue(self, field, html, stype=None):
        section = self.findbyre('(?s)"field-label">[^<>]*%s:[^<>]*</div>(.*?)</div><div>'%field, html)
        if section:
            return self.findbyre('>\s*(\w[^<>]+)<', section, stype)

    def findnames(self, html):
        return [self.findbyre('"og:title"[^<>]*content="(.*?)"', html)]

    def finddescription(self, html):
        return self.getvalue('Listed as', html)

    def findlongtext(self, html):
        result = self.findbyre('(?s)(?:<div id="field-group-authors-bio"[^<>]*>|<h3><span[^<>]*>Publications and Prizes)(.*?)</article>', html)
        if result:
            return result.replace("&nbsp;", " ").replace("&lt;", "<").replace("&gt;", ">")
    
    def findinstanceof(self, html):
        return "Q5"

    def findoccupations(self, html):
        section = self.getvalue('Listed as', html)
        if section:
            return [self.getdata('occupation', part) for part in section.split(',')]

    def findlanguagesspoken(self, html):
        section = self.getvalue('Fluent in', html)
        if section:
            return [self.getdata('language', part) for part in section.split(',')]

    def findbirthplace(self, html):
        return self.getvalue('Born in', html, 'city') or self.findbyre('born in ([\w\s]+)', html, 'city')

    def findethnicities(self, html):
        section = self.findbyre('Identifies as:[^<>]*(?:<[^<>]*>)*([^<>]*)</', html)
        if section:
            return self.findallbyre('([^,]+)', section, 'ethnicity (us)', skips = ['religion'])

    def findreligions(self, html):
        section = self.findbyre('Identifies as:[^<>]*(?:<[^<>]*>)*([^<>]*)</', html)
        if section:
            return self.findallbyre('([^,]+)', section, 'religion', skips = ['ethnicity', 'ethnicity (us)'])

    def findwebsite(self, html):
        return self.findbyre('Website:[^<>]*(?:<[^<>]*>)*<a[^<>]*href="([^<>]*?)"', html)


class ScottishArchitectsAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P5308'
        self.dbid = 'Q16973743'
        self.dbname = 'Dictionary of Scottish Architects'
        self.urlbase = 'http://www.scottisharchitects.org.uk/architect_full.php?id={id}'
        self.hrtre = '</h1>(.*?)(?:<h1|<td[^<>]*>Bio Notes)'
        self.language = 'en'

    def findnames(self, html):
        return [self.findbyre('<b>(.*?)<', html)]

    def findlongtext(self, html):
        return self.findbyre('Bio Notes:(.*?)</tr>', html)

    def findinstanceof(self, html):
        return 'Q5'

    def findoccupations(self, html):
        section = self.findbyre('Designation:(.*?)</tr>', html)
        if section:
            result = []
            for subsection in self.findallbyre('>([^<>]*)</td', section):
                result += self.findallbyre('([\w\s]+)', subsection, 'occupation')
            return result

    def findbirthdate(self, html):
        return self.findbyre('Born:</td>.*?>(?:c\.)?([^<>]*)</td>', html)

    def finddeathdate(self, html):
        return self.findbyre('Died:</td>.*?>(?:c\.)?([^<>]*)</td>', html)

    def findresidences(self, html):
        section = self.findbyre('Addresses</h2>(<table.*?</table>)', html)
        if section:
            return self.findallbyre("<tr[^<>]*><td><img src='images/table_item.gif'[^<>]*></td><td>[^<>]*?([^<>,]*(?:,[^<>,]*)?)<", section, 'city')


class SFAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P5357'
        self.dbid = 'Q5099499'
        self.dbname = 'Encyclopedia of Science Fiction'
        self.urlbase = 'http://www.sf-encyclopedia.com/entry/{id}'
        self.hrtre = '(<p>.*?)<h2'
        self.language = 'en'

    def findlongtext(self, html):
        return self.findbyre('(?s)(<p>.*?)<h\d', html)

    def findbirthdate(self, html):
        return self.findbyre('<b>born</b>[^<>]*?([^<>:]*)<', html)

    def finddeathdate(self, html):
        return self.findbyre('<b>died</b>[^<>]*?([^<>:]*)<', html)

    def findbirthplace(self, html):
        return self.findbyre('<b>born</b>([^<>]*):', html, 'city')
        
    def finddeathplace(self, html):
        return self.findbyre('<b>died</b>([^<>]*):', html, 'city')

    def findnationality(self, html):
        return self.findbyre('<p>\([\s\d\-]+\)\s*(\w+)', html, 'country')

    def findoccupations(self, html):
        section = self.findbyre('<p>\([\s\d\-]+\)([\w\s]+)', html)
        if section:
            return self.findallbyre('(\w+)', section, 'occupation')

    def findmixedrefs(self, html):
        return [
            ('P1233', self.findbyre('http://www.isfdb.org/cgi-bin/ea.cgi\?(\d+)', html))
            ]


class NatGeoCanadaAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P5368'
        self.dbid = None
        self.dbname = 'National Gallery of Canada'
        self.urlbase = 'https://www.gallery.ca/collection/artist/{id}'
        self.hrtre = '(<div[^<>]* group-right .*?clearfix">)'
        self.language = 'en'

    def findnames(self, html):
        return self.findallbyre('>Name(?:<[^<>]*>|\s)*(.*?)<', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)(<div class="wrapper-max-width.*?)<div class="col-xs-12', html)

    def finddescription(self, html):
        return self.findbyre('<meta name="description" content="(.*?)"', html)

    def findbirthplace(self, html):
        return self.findbyre('Born</div>(.*?)<', html, 'city')

    def findbirthdate(self, html):
        return self.findbyre('Born</div>[^<>]*(?:<[^<>]*>)*([\d\-]+)<', html)

    def finddeathplace(self, html):
        return self.findbyre('Died</div>(.*?)<', html, 'city')

    def finddeathdate(self, html):
        return self.findbyre('Died</div>[^<>]*(?:<[^<>]*>)*([\d\-]+)<', html)

    def findnationalities(self, html):
        section = self.findbyre('>Nationality(?:<[^<>]*>|\s)*(.*?)<', html)
        if section:
            return self.findallbyre('([^,]+)', re.sub('\(.*?\)', ',', section), 'country')

    def findethnicity(self, html):
        section = self.findbyre('>Nationality(?:<[^<>]*>|\s)*(.*?)<', html)
        if '(' in section:
            return self.findbyre('(.*)', section, 'ethnicity')

    def findresidences(self, html):
        return self.findallbyre('lives ([^"<>]+)', html, 'city')

class FantasticFictionAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P5408'
        self.dbid = 'Q21777935'
        self.dbname = 'Fantastic Fiction'
        self.urlbase = 'https://www.fantasticfiction.com/{id}/'
        self.hrtre = '<div class="authorheading">(.*?)</div>'
        self.language = 'en'
        self.escapehtml = True

    def findinstanceof(self, html):
        return 'Q5'

    def findnames(self, html):
        result = [
            self.findbyre('<title>(.*?)</title>', html)
            ]
        result += self.findallbyre('<h1[^<>]*>(.*?)</h1>', html)
        result += self.findallbyre('<b>(.*?)</b>', html)
        result += self.findallbyre('>aka\s*<a[^<>]*>(.*?)<', html)
        return result

    def findlongtext(self, html):
        return self.findbyre('(?s)<div class="authorheading">.*?</div>(.*?)<div', html)

    def finddescription(self, html):
        prepart = self.findbyre('(?s)<div class="authorheading">.*?</div>(.*?)\.', html)
        return self.findbyre('(.*)', prepart)

    def findbirthdate(self, html):
        return self.findbyre('>b\.(?:<[^<>]*>)*(.+?)<', html)

    def findnationality(self, html):
        return self.findbyre('</h1><br><a[^<>]*>(.*?)<', html, 'country') or\
               self.findbyre('</h1><br><img alt="([^"]+)\s', html, 'country')

    def findsiblings(self, html):
        return self.findallbyre('(?:Brother|Sister) of <a[^<>]*>(.*?)<', html, 'person')

    def findfather(self, html):
        for person in self.findallbyre('(?:Son|Daughter) of <a[^<>]*>(.*?)<', html, 'male-person'):
            if person:
                return person
            
    def findmother(self, html):
        for person in self.findallbyre('(?:Son|Daughter) of <a[^<>]*>(.*?)<', html, 'female-person'):
            if person:
                return person
        
    def findchildren(self, html):
        return self.findallbyre('(?:Father|Mother) of <a[^<>]*>(.*?)<', html, 'person')

    def findgenres(self, html):
        section = self.findbyre('Genres: (.*)', html)
        if section:
            return self.findallbyre('<a[^<>]*>(.*?)<', section, 'genre')

    def findawards(self, html):
        section = self.findbyre('(?s)>Awards<.*?<table[^<>]*>(.*?)</table>', html)
        if section:
            return self.findallbyre('<a[^<>]*>(?:<[^<>]*>)*([^<>]*)(?:<[^<>]*>)*</a>[^<>]*winner', html, 'award')
        
    def findnominations(self, html):
        section = self.findbyre('(?s)>Awards<.*?<table[^<>]*>(.*?)</table>', html)
        if section:
            return self.findallbyre('<a[^<>]*>(?:<[^<>]*>)*([^<>]*)(?:<[^<>]*>)*</a>[^<>]*nominee', html, 'award')

   
class WhonameditAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P5415'
        self.dbid = 'Q66683'
        self.dbname = 'Who named it?'
        self.urlbase = 'http://www.whonamedit.com/doctor.cfm/{id}.html'
        self.hrtre = '(<h1.*?<div id="description">.*?</div>)'
        self.language = 'en'

    def findnames(self, html):
        return [
            self.findbyre('<h1[^<>]*>(.*?)<', html),
            self.findbyre('(?s)</h2>\s*<p><strong>(.*?)<', html)
            ]

    def findlongtext(self, html):
        return self.findbyre('(?s)(<div id="description">.*?</div>)', html)

    def findinstanceof(self, html):
        return "Q5"

    def findbirthdate(self, html):
        return self.findbyre('born (\w+ \d+, \d+)', html) or\
               self.findbyre('(?s)Born</td>\s*<td>(.*?)<', html)

    def finddeathdate(self, html):
        return self.findbyre('died (\w+ \d+, \d+)', html) or\
               self.findbyre('(?s)Died</td>\s*<td>(.*?)<', html)

    def findbirthplace(self, html):
        return self.findbyre('born [^<>]*?\d, ([A-Za-z][^<>]*?);', html, 'city')

    def finddeathplace(self, html):
        return self.findbyre('died [^<>]*?\d, ([A-Za-z][^<>]*?)\.', html, 'city')

    def findnationality(self, html):
        return self.findbyre('(?s)<div id="short-description">\s*(\w+)', html, 'country')

    def findoccupations(self, html):
        section = self.findbyre('(?s)<div id="short-description">\s*\w+([^<>]*?), born', html)
        if section:
            return self.findallbyre('(\w{4,})', section, 'occupation')


class TradingCardAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P5421'
        self.dbid = None
        self.dbname = 'Trading Card Database'
        self.urlbase = 'https://www.tradingcarddb.com/Person.cfm/pid/{id}/'
        self.hrtre = '(<h4.*?)</div>'
        self.language = 'en'

    def findnames(self, html):
        return self.findallbyre('<h4>(.*?)<', html) +\
               self.findallbyre('(?s)</h4>\s*<strong>(.*?)<', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)(<h4.*?)</div>', html)

    def findbirthdate(self, html):
        return self.findbyre('Born:</strong>\s*(\w+ \d+, \d+)', html)
    
    def finddeathdate(self, html):
        return self.findbyre('Died:</strong>\s*(\w+ \d+, \d+)', html)

    def findbirthplace(self, html):
        return self.findbyre('Born:</strong>[^<>]* in ([^<>]*)', html)

    def finddeathplace(self, html):
        return self.findbyre('Died:</strong>[^<>]* in ([^<>]*)', html)

    def findschools(self, html):
        return self.findallbyre('<strong>College:</strong>(.*?)<', html)

    def findsportteams(self, html):
        return self.findallbyre('"/Team\.cfm/[^<>"]+">(.*?)</a>', html)

    def findsports(self, html):
        section = self.findbyre('<ol class="breadcrumb">(.*?)</ol>', html)
        if section:
            return self.findallbyre('"/ViewAll\.cfm/[^<>"]*">(.*?)<', section, 'sport (US)')


class BedethequeAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P5491'
        self.dbid = 'Q2876969'
        self.dbname = 'Bedetheque'
        self.urlbase = 'https://www.bedetheque.com/auteur-{id}-BD-.html'
        self.hrtre = '<ul class="auteur-info">(.*?)</ul>'
        self.language = 'fr'

    def findinstanceof(self, html):
        return 'Q5'

    def findnames(self, html):
        return self.findallbyre('<h2>(.*?)<', html) +\
               [self.findbyre('<label>Pseudo :</label>(.*?)</li>', html)]

    def findfirstname(self, html):
        return self.findbyre('<label>Prénom :</label>(?:<span>)?(.*?)</', html, 'firstname')

    def findlastname(self, html):
        return self.findbyre('<label>Nom :</label>(?:<span>)?(.*?)</', html, 'lastname')

    def findlongtext(self, html):
        return self.findbyre('(?s)<h3>Sa biographie</h3>.*?<div class="block-big block-big-last">(.*?)</div>', html)

    def findpseudonyms(self, html):
        return [self.findbyre('<label>Pseudo :</label>(.*?)</li>', html)]

    def findbirthdate(self, html):
        return self.findbyre('<label>Naissance :</label>le ([\d/]+)', html)

    def finddeathdate(self, html):
        return self.findbyre('<li><label>Décès :</label>le ([\d/]+)', html)

    def findnationality(self, html):
        return self.findbyre('<span class="pays-auteur">\(?(.*?)\)?<', html, 'country')
        
    def findwebsite(self, html):
        return self.findbyre('Site internet :.*?"(.*?)"', html)
    

class OmdbAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P5534'
        self.dbid = 'Q27653527'
        self.dbname = 'Open Media Database'
        self.urlbase = 'https://www.omdb.org/person/{id}'
        self.hrtre = '<h3>Daten</h3>(.*?)<div class="headline-box">'
        self.language = 'de'

    def findinstanceof(self, html):
        return 'Q5'

    def findnames(self, html):
        result = self.findallbyre('<h2>(.*?)</h2>', html)
        section = self.findbyre('(?s)<h3>auch bekannt als</h3>(.*?)<div class="headline-box">', html)
        if section:
            result += self.findallbyre('(?s)>([^<>]*)<', section)
        return result

    def finddescriptions(self, html):
        return self.findallbyre('<meta content="(.*?)"', html) +\
               [self.findbyre('(?s)<div class="parent-breadcrumb">.*?</div>\s*<h2>[^<>]*</h2>\s*<h3>(.*?)</h3>', html)]

    def findlongtext(self, html):
        return self.findbyre('(?s)<p id="abstract">(.*?)</div>', html)

    def findoccupations(self, html):
        section = self.findbyre('(?s)<div class="parent-breadcrumb">.*?</div>\s*<h2>[^<>]*</h2>\s*<h3>(.*?)</h3>', html)
        if section:
            return self.findallbyre('">([^<>]*)</a>', section, 'occupation')

    def findgender(self, html):
        return self.findbyre('(?s)<div class="title">Geschlecht:</div>\s*<div class="value">(.*?)<', html, 'gender')

    def findbirthdate(self, html):
        return self.findbyre('(?s)<div class="title">Geburtstag:</div>\s*<div class="value">(.*?)<', html)

    def findbirthplace(self, html):
        return self.findbyre('(?s)<div class="title">Geburtsort:</div>\s*<div class="value">(.*?)<', html, 'city')

    def finddeathdate(self, html):
        return self.findbyre('(?s)<div class="title">Todestag:</div>\s*<div class="value">(.*?)<', html)

    def finddeathplace(self, html):
        return self.findbyre('(?s)<div class="title">Todesort:</div>\s*<div class="value">(.*?)<', html, 'city')

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html)


class NoosfereAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P5570'
        self.dbid = None
        self.dbname = 'NooSFere'
        self.urlbase = 'https://www.noosfere.org/livres/auteur.asp?numauteur={id}&Niveau=bio'
        self.hrtre = '<td[^<>]*>[^<>]*Bio/Infos.*?(<.*?</TABLE>.*?</tr>)'
        self.language = 'fr'
        self.escapeunicode = True

    def prepare(self, html):
        return html.replace('\\n', '\n').replace('\\t', ' ').replace('\\r', '').replace("\\'", "'").replace('\\xe9', 'é').replace('\\xe8', 'è').replace("\\xea", 'ê').replace('&nbsp;', ' ')

    def findinstanceof(self, html):
        return 'Q5'

    def findnames(self, html):
        section = self.findbyre('Pseudonyme\(s\)(.*?)</DIV>', html)
        if section:
            result = self.findallbyre('>([^<>]*)<', section)
            return [name.title() for name in result]

    def findlongtext(self, html):
        return self.findbyre('<!-- Corps de la page -->(.*?)</TABLE>', html)

    def findbirthdate(self, html):
        return self.findbyre('Naissance\s?:[^<>]*?([^<>,]*?)\.?<', html)

    def findbirthplace(self, html):
        return self.findbyre('Naissance\s?:([^<>]*),', html, 'city')
        
    def finddeathdate(self, html):
        return self.findbyre('D.c.s :[^<>]*?([^<>,]*?)\.?<', html)

    def finddeathplace(self, html):
        return self.findbyre('D.c.s :([^<>]*),', html, 'city')
        
    def findnationality(self, html):
        return self.findbyre("'Auteurs du m.me pays'>(.*?)<", html, 'country')

    def findawards(self, html):
        return self.findallbyre('&numprix=\d+">(.*?)<', html, 'award')

    def findwebsite(self, html):
        return self.findbyre("'([^<>']*)'>Site officiel", html)

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html)


class ArtcyclopediaAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P5597'
        self.dbid = 'Q3177776'
        self.dbname = 'Artcyclopedia'
        self.urlbase = 'http://www.artcyclopedia.com/artists/{id}.html'
        self.hrtre = '(<H1.*?)<TABLE WIDTH="100%"'
        self.language = 'en'
        self.escapehtml = True

    def prepare(self, html):
        return html.replace('&nbsp;', ' ')

    def findinstanceof(self, html):
        return 'Q5'

    def findnames(self, html):
        return self.findallbyre('<H1[^<>]*>(.*?)<', html) +\
               self.findallbyre('Also known as:[^<>]*(?:<[^<>]*>)*([^<>]+)</', html)
    
    def finddescription(self, html):
        result = self.findbyre('<B>(.*?)</B>', html)
        if result:
            return self.TAGRE.sub(' ', result).strip('[]')

    def findlongtext(self, html):
        return self.findbyre('(?s)(<H1.*?)<TABLE WIDTH="100%"', html)

    def findmovements(self, html):
        section = self.findbyre('<B>(.*?)</B>', html)
        if section:
            return self.findallbyre('<A[^<>]*>(.*?)<', section, 'movement')

    def findnationality(self, html):
        return self.findbyre('<B>\[(\w+)', html, 'country')

    def findbirthdate(self, html):
        return self.findbyre('(\d+)-\d*\]<B>', html)

    def finddeathdate(self, html):
        return self.findbyre('-(\d+)\]<B>', html)

    def findincollections(self, html):
        section = self.findbyre('(?s)><A NAME="museums">(.*?)<A NAME', html)
        if section:
            return self.findallbyre('>([^<>]*)</A>', section, 'museum')

    
class AcademieFrancaiseAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P5645'
        self.dbid = None
        self.dbname = 'Académie française'
        self.urlbase = 'http://www.academie-francaise.fr/{id}'
        self.hrtre = '(<h1>.*?)<div id="footer"'
        self.language = 'fr'

    def findnames(self, html):
        return [
            self.findbyre('<title>(.*?)[\|<]', html),
            self.findbyre('(?s)<h1>(.*?)<', html)
            ]

    def findlongtext(self, html):
        return self.findbyre('(?s)(<h2>\s*Prix.*?)<div id="footer"', html)

    def findawards(self, html):
        section = self.findbyre('(?s)(<h2>\s*Prix.*?)<div id="footer"', html)
        if section:
            return self.findallbyre('">(.*?)</a>', section, 'award')


class AngelicumAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P5731'
        self.dbid = None
        self.dbname = 'Angelicum'
        self.urlbase = 'https://pust.urbe.it/cgi-bin/koha/opac-authoritiesdetail.pl?marc=1&authid={id}'
        self.hrtre = '<h1>Entry[^<>]*</h1>(.*?)</div>'
        self.language = 'it'

    def instanceof(self, html):
        return self.findbyre(' di ([^<>]*)</title>', html, 'instanceof')

    def findnames(self, html):
        return self.findallbyre('(?s)<b>Nome d[^<>]*</b>(.*?)</', html)

    def findbirthdate(self, html):
        return self.findbyre('(?s)<b>Data di nascita:</b>(.*?)</', html)

    def finddeathdate(self, html):
        return self.findbyre('(?s)<b>Data di morte:</b>(.*?)</', html)

    def findlanguagesspoken(self, html):
        return self.findallbyre('(?s)<b>Codice di lingua:</b>(.*?)</', html, 'language')

    def findnationalities(self, html):
        return self.findallbyre('(?s)<b>Luogo di nascita:</b>(.*?)</', html, 'country')

    def findgender(self, html):
        return self.findbyre('(?s)<b>Sesso:</b>(.*?)</', html, 'gender')

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html, includesocial=False)
        

class PuscAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P5739'
        self.dbid = None
        self.dbname = 'PUSC'
        self.urlbase = 'http://catalogo.pusc.it/cgi-bin/koha/opac-authoritiesdetail.pl?authid={id}&marc=1'
        self.hrtre = '</h1>(.*?)</div>'
        self.language = 'it'

    def findnames(self, html):
        return self.findallbyre('(?s) name[^<>]*:</b>(.*?)[<\(]', html)

    def findlongtext(self, html):
        return '\n'.join(self.findallbyre('(?s)Source citation:</b>(.*?)<', html))

    def findbirthdate(self, html):
        return self.findbyre('(?s)Birth date:</b>(.*?)<', html)

    def finddeathdate(self, html):
        return self.findbyre('(?s)Death date:</b>(.*?)<', html)

    def findgender(self, html):
        return self.findbyre('(?s)Gender:</b>(.*?)<', html, 'gender')

    def getcode(self, code, html):
        return self.findbyre('(?s)<b>Source of number or code:</b>\s*%s</p>\s*<p><b>Standard number or code:</b>\s*(.*?)</p>'%code, html)
    
    def findmixedrefs(self, html):
        return [
            ('P214', self.getcode('viaf', html)),
            ('P269', self.getcode('idref', html)),
            ('P244', self.getcode('lccn', html)),
            ] +\
            self.finddefaultmixedrefs(html, includesocial=False)

    def findisni(self, html):
        return self.getcode('isni', html)

        
class CwaAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P5747'
        self.dbid = None
        self.dbname = 'CWA'
        self.urlbase = 'https://thecwa.co.uk/find-an-author/{id}/'
        self.hrtre = '(<h1.*?)<h3>Books'
        self.language = 'en'

    def findnames(self, html):
        return self.findbyre('>([^<>]*)</h1>', html)

    def findinstanceof(self, html):
        return 'Q5'

    def findoccupations(self, html):
        return ['Q36180']

    def findwebsite(self, html):
        return self.findbyre('"([^"<>]*)">Website<', html)

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html)

    def findawards(self, html):
        section = self.findbyre('(?s)<h3>Other Awards</h3>(.*?)<h\d', html)
        if section:
            parts = self.findallbyre('>([^<>]*)</p>', section)
            result = []
            for part in parts:
                result += self.findallbyre('([^,]+)', part, 'award')
            return result


class LetterboxdAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P6127'
        self.dbid = 'Q18709181'
        self.dbname = 'Letterboxd'
        self.urlbase = 'view-source:https://letterboxd.com/film/{id}/'
        self.hrtre = '(<div id="tabbed-content".*?)<p class="text-link '
        self.language = 'en'
        self.escapehtml = True

    def findinstanceof(self, html):
        return 'Q11424'

    def findlongtext(self, html):
        return self.findbyre('<meta name="description" content="(.*?)"', html)

    def finddescriptions(self, html):
        result = [
            self.findbyre('<meta property="og:title" content="(.*?)"', html),
            self.findbyre('<title>&\w+;([^<>]*). Reviews, film', html)
        ]
        section = self.findbyre('(?s)<h3><span>Alternative Titles</span></h3>.*?<p>(.*?)</p>', html)
        if section:
            result += section.split(' - ')
        return result

    def findnames(self, html):
        return [ self.findbyre('<meta property="og:title" content="([^<>\(\)"]+)', html) ]

    def findcast(self, html):
        section = self.findbyre('(?s)(<div class="cast-list.*?</div>)', html)
        if section:
            return self.findallbyre('<span itemprop="name">(.*?)<', html, 'actor')

    def findmoviedirectors(self, html):
        section = self.findbyre('(?s)<h3><span>Director</span></h3>(.*?)</div>', html)
        if section:
            return self.findallbyre('">([^<>]*)</a>', html, 'filmmaker')

    def findscreenwriters(self, html):
        section = self.findbyre('(?s)<h3><span>Writers</span></h3>(.*?)</div>', html)
        if section:
            return self.findallbyre('">([^<>]*)</a>', html, 'filmmaker')
        
    def findmovieeditors(self, html):
        section = self.findbyre('(?s)<h3><span>Editors</span></h3>(.*?)</div>', html)
        if section:
            return self.findallbyre('">([^<>]*)</a>', html, 'filmmaker')
        
    def findproducers(self, html):
        section = self.findbyre('(?s)<h3><span>Producers</span></h3>(.*?)</div>', html)
        if section:
            return self.findallbyre('">([^<>]*)</a>', html, 'filmmaker')

    def finddirectorsphotography(self, html):
        section = self.findbyre('(?s)<h3><span>Cinematography</span></h3>(.*?)</div>', html)
        if section:
            return self.findallbyre('">([^<>]*)</a>', html, 'filmmaker')
        
    def findproductiondesigners(self, html):
        section = self.findbyre('(?s)<h3><span>Production Design</span></h3>(.*?)</div>', html)
        if section:
            return self.findallbyre('">([^<>]*)</a>', html, 'filmmaker')
        
    def findcomposers(self, html):
        section = self.findbyre('(?s)<h3><span>Composer</span></h3>(.*?)</div>', html)
        if section:
            return self.findallbyre('">([^<>]*)</a>', html, 'composer')
        
    def findsounddesigners(self, html):
        section = self.findbyre('(?s)<h3><span>Sound</span></h3>(.*?)</div>', html)
        if section:
            return self.findallbyre('">([^<>]*)</a>', html, 'filmmaker')
        
    def findcostumedesigners(self, html):
        section = self.findbyre('(?s)<h3><span>Costume</span></h3>(.*?)</div>', html)
        if section:
            return self.findallbyre('">([^<>]*)</a>', html, 'costumer')
        
    def findmakeupartists(self, html):
        section = self.findbyre('(?s)<h3><span>Make-Up</span></h3>(.*?)</div>', html)
        if section:
            return self.findallbyre('">([^<>]*)</a>', html, 'costumer')

    def findprodcoms(self, html):
        section = self.findbyre('(?s)<h3><span>Studios</span></h3>(.*?)</div>', html)
        if section:
            return self.findallbyre('">([^<>]*)</a>', html, 'filmcompany')

    def findorigcountries(self, html):
        section = self.findbyre('(?s)<h3><span>Country</span></h3>(.*?)</div>', html)
        if section:
            return self.findallbyre('">([^<>]*)</a>', html, 'country')
        
    def findoriglanguages(self, html):
        section = self.findbyre('(?s)<h3><span>Language</span></h3>(.*?)</div>', html)
        if section:
            return self.findallbyre('">([^<>]*)</a>', html, 'language')
        
    def findgenres(self, html):
        section = self.findbyre('(?s)<h3><span>Language</span></h3>(.*?)</div>', html)
        if section:
            return self.findallbyre('">([^<>]*)</a>', html, 'genre')
        
    def finddurations(self, html):
        result = self.findbyre('(\d+)(?:&nbsp;|\s+)mins', html)
        if result:
            return [ result.replace('&nbsp;', ' ') ]
    
        
class BritishExecutionsAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P6167'
        self.dbid = None
        self.dbname = 'British Executions'
        self.urlbase = 'http://www.britishexecutions.co.uk/execution-content.php?key={id}'
        self.hrtre = '(<h1>.*?)<div'
        self.language = 'en'
        self.escapehtml = True

    def findinstanceof(self, html):
        return 'Q5'

    def findlongtext(self, html):
        return self.findbyre('(?s)<h1>.*?<div class="">(.*?)</div>', html)

    def findnames(self, html):
        return [self.findbyre('<h1[^<>]*>(?:<[^<>]*>)*([^<>]+)<', html)]

    def findgender(self, html):
        return self.findbyre('<strong>Sex:</strong>(.*?)<', html, 'gender')

    def finddeathdate(self, html):
        return self.findbyre('<strong>Date Of Execution:</strong>(.*?)<', html)

    def findcrimes(self, html):
        return [self.findbyre('<strong>Crime:</strong>(.*?)<', html, 'crime')]

    def findmannerdeath(self, html):
        return 'Q8454'

    def findcausedeath(self, html):
        return self.findbyre('<strong>Method:</strong>(.*?)<', html, 'execution-method')
    
    def finddeathplace(self, html):
        return self.findbyre('<strong>Execution Place:</strong>(.*?)<', html, 'city')


class BdfaAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P6188'
        self.dbid = 'Q19368470'
        self.dbname = 'Base de Datos del Futbol Argentino'
        self.urlbase = 'https://www.bdfa.com.ar/jugador.asp?codigo={id}'
        self.hrtre = '<!-- DATOS JUGADOR -->(.*?)<!-- FIN DATOS JUGADOR -->'
        self.language = 'es'
        self.escapehtml = True

    def findnames(self, html):
        return self.findallbyre('<strong>(.*?)<', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)Resumen</h4>(.*?)</div>', html)

    def findteampositions(self, html):
        return self.findbyre('(?s)<strong>Posición:</strong>(.*?)<', html, 'footballposition')

    def findweight(self, html):
        return self.findbyre('(?s)<strong>Peso:</strong>\s*(\d+\s*kg)\.', html)

    def findheight(self, html):
        return self.findbyre('(?s)<strong>Altura:</strong>\s*(\d+\s*m)ts', html)
    
    def findnationality(self, html):
        return self.findbyre('(?s)<strong>Nacionalidad:</strong>(.*?)<', html, 'country')

    def findbirthdate(self, html):
        return self.findbyre('(?s)<strong>Fecha de nacimiento:</strong>(.*?)[<\(]', html)

    def findbirthplace(self, html):
        return self.findbyre('(?s)<strong>Lugar de Nacimiento:</strong>(.*?)<', html, 'city')

    def findsportteams(self, html):
        return self.findallbyre('<a href="lista_jugadores[^<>]*>(.*?)<', html, 'footballteam')


class AustrianBiographicalAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P6194'
        self.dbid = 'Q25666'
        self.dbname = 'Österreichisches Biographisches Lexikon'
        self.urlbase = 'http://www.biographien.ac.at/oebl/oebl_{id}.xml'
        self.hrtre = '<div id="Langtext">(.*?<span class="lemmatext">.*?</span>)'
        self.language = 'de'

    def findnames(self, html):
        return [self.findbyre('<meta name="DC.Title" content="(.*?)[";]', html)]

    def finddescriptions(self, html):
        return [
            self.findbyre('<meta name="DC.Description" content="(.*?)"', html),
            self.findbyre('(?s)<span id="Schlagwort"[^<>]*>(.*?)<p>', html),
            self.findbyre('<span class="lemmatext">(.*?)</span>', html)
            ]

    def findlongtext(self, html):
        return self.findbyre('(?s)<div id="Langtext">(.*?)</div>', html)
        
    def findbirthplace(self, html):
        return self.findbyre(' \* (.*?),', html, 'city')

    def findbirthdate(self, html):
        return self.findbyre(' \* .*?,([^,;<>]*);', html)

    def finddeathplace(self, html):
        return self.findbyre(' † (.*?),', html, 'city')

    def finddeathdate(self, html):
        return self.findbyre(' † .*?,([^,;<>]*)\.', html)

    def findoccupations(self, html):
        section = self.findbyre('<span id="Schlagwort" class="lemma2">[^<>,]*,(.*?)<', html)
        if section:
            result = []
            parts = section.split(' und ')
            for part in parts:
                result += self.findallbyre('([\w\s]+)', part, 'occupation')
            return result

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html)


class BdelAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P6231'
        self.dbid = None
        self.dbname = 'Base de données des élites suisses'
        self.urlbase = 'https://www2.unil.ch/elitessuisses/index.php?page=detailPerso&idIdentite={id}'
        self.hrtre = '<H1>(.*?)<h1'
        self.language = 'fr'
        self.escapehtml = True

    def getvalue(self, field, html, dtype=None):
        return self.findbyre('(?s)<td[^<>]*>\s*%s\s*:\s*</td>\s*<td[^<>]*>(.*?)</td>'%field, html, dtype)
 
    def findnames(self, html):
        return self.findallbyre('<H1>(.*?)[\(<]', html)

    def finddescription(self, html):
        return self.getvalue('Principales professions', html)

    def findfirstname(self, html):
        return self.getvalue('Prénom', html, 'firstname')

    def findlastname(self, html):
        return self.getvalue('Nom', html, 'lastname')

    def findgender(self, html):
        return self.getvalue('Sexe', html, 'gender')

    def findbirthdate(self, html):
        return self.findbyre('Naissance:\s*([\d\.]+)', html)

    def finddeathdate(self, html):
        return self.findbyre('Décès:\s*([\d\.]+)', html)

    def findbirthplace(self, html):
        return self.getvalue('Lieu naissance', html, 'city')

    def findnationality(self, html):
        return self.getvalue('Nationalité', html, 'country')

    def findoccupations(self, html):
        section = self.getvalue('Principales professions', html)
        if section:
            return self.findallbyre('([^,]+)', section, 'occupation')

    def findranks(self, html):
        section = self.getvalue('Officier\s*\?', html)
        if section:
            return self.findallbyre('([^,/]+)', section, 'rank')

    def findparties(self, html):
        section = self.findbyre('(?s)<b>parti</b>(.*?)</table>', html)
        if section:
            return self.findallbyre('(?s)<td>([^<>]*)</td>\s*<td[^<>]*>[^<>]*</td>\s*</tr>', section, 'party')

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html)


class WhoSampledAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P6517'
        self.dbid = 'Q7997133'
        self.dbname = 'whosampled.com'
        self.urlbase = 'https://www.whosampled.com/{id}/'
        self.hrtre = '(<h1.*?)<script>'
        self.language = 'en'

    def findnames(self, html):
        section = self.findbyre('(?s)(<h1.*?)<script>', html) or self.findbyre('(?s)(.*?)<script>', html) or html
        return self.findallbyre('itemprop="\w*[nN]ame"[^<>]*>(.*?)<', section) +\
               self.findallbyre('itemprop="sameAs"[^<>]*>(.*?)<', section)

    def findlongtext(self, html):
        return self.findbyre('(?s)(<h1.*?)<script>', html)

    def findmemberships(self, html):
        return self.findallbyre('itemprop="memberOf"[^<>]*>(.*?)<', html, 'group')

    def findparts(self, html):
        return self.findallbyre('itemprop="member"[^<>]*>(.*?)<', html, 'musician')

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html, includesocial=False)

    def findwebsite(self, html):
        return self.findbyre('href="([^"<>]+)"[^<>]*>Official Site<', html)


class MutualAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P6578'
        self.dbid = 'Q22907130'
        self.dbname = 'MutualArt'
        self.urlbase = 'https://www.mutualart.com/Artist/wd/{id}'
        self.hrtre = '(<h1.*?)<div\s*preferences'
        self.language = 'en'

    def findnames(self, html):
        return [ self.findbyre('(?s)<h1[^<>]*>(.*?)<', html) ]
    
    def findlongtext(self, html):
        return self.findbyre('(?s)<p class="bio"[^<>]*>(.*?)</div>', html)

    def findnationality(self, html):
        return self.findbyre('(?s)>([^<>]*)<span class="separator">', html, 'country')

    def findbirthdate(self, html):
        return self.findbyre('(?s)<span class="separator">.</span>(.*?)[\-<]', html)

    def finddeathdate(self, html):
        return self.findbyre('(?s)<span class="separator">.</span>[^<>]*-(.*?)<', html)


class AbartAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P6844'
        self.dbid = 'Q10855166'
        self.dbname = 'AbART'
        self.urlbase = 'https://en.isabart.org/person/{id}'
        self.hrtre = '(<h2.*?)(?:<strong>word:|<strong>notes:|end \.detail-content)'
        self.language = 'cs'

    def findnames(self, html):
        return [self.findbyre('<h2>(.*?)</h2>', html)]

    def findlanguagedescriptions(self, html):
        return [('en', self.findbyre('<br>([^<>]*)</p>', html))]

    def findlongtext(self, html):
        return self.findbyre('(?s)<strong>notes:</strong>(.*?)</p>', html)

    def findbirthdate(self, html):
        return self.findbyre('\*\s*<span>(.*?)</span>', html)

    def findbirthplace(self, html):
        return self.findbyre('\*\s*<span>[^<>]*</span>,\s*<span>(.*?)</span>', html, 'city')

    def finddeathdate(self, html):
        return self.findbyre('&dagger;\s*<span>(.*?)</span>', html)

    def finddeathplace(self, html):
        return self.findbyre('&dagger;\s*<span>[^<>]*</span>,\s*<span>(.*?)</span>', html, 'city')

    def findoccupations(self, html):
        section = self.findbyre('<br>([^<>]*)</p>', html)
        if section:
            return self.findallbyre('([^,]*)', section, 'occupation')

    def findnationality(self, html):
        return self.findbyre('<strong>nationality:</strong>([^<>]*)', html, 'country')

    def findgender(self, html):
        return self.findbyre('<strong>sex:</strong>([^<>]*)', html, 'gender')


class IntraTextAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P6873'
        self.dbid = 'Q3800762'
        self.dbname = 'IntraText'
        self.urlbase = 'http://www.intratext.com/Catalogo/Autori/AUT{id}.HTM'
        self.hrtre = '()'
        self.language = 'en'
        self.escapehtml = True

    def findnames(self, html):
        return [self.findbyre('<b>(.*?)<', html)] +\
            self.findallbyre('<FONT[^<>]*>(.*?)<', html)

#    def findlanguagesspoken(self, html):
#        return self.findallbyre('<span class=LI>([^<>]*) - ', html, 'language')

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html, includesocial=False)


class RepertoriumAnalyzer(Analyzer):
    def setup(self):
        self.dbproperty = 'P7032'
        self.dbid = 'Q65032487'
        self.dbname = 'Repertorium van ambtsdragers en ambtenaren'
        self.urlbase = 'http://resources.huygens.knaw.nl/repertoriumambtsdragersambtenaren1428-1861/app/personen/{id}'
        self.hrtre = '(<h1 class="naam">)<h2'
        self.language = 'nl'

    def findinstanceof(self, html):
        return 'Q5'

    def findnames(self, html):
        return [self.findbyre('(?s)<h1 class="naam">(.*?)<', html)]

    def findlongtext(self, html):
        return self.findbyre('(?s)(<h1 class="naam">.*?)<h2>bron', html)
    
    def findbirthdate(self, html):
        return self.findbyre('(?s)geboren:\s*([\d\-]+)', html)

    def finddeathdate(self, html):
        return self.findbyre('(?s)overleden:\s*([\d\-]+)', html)

    def findbirthplace(self, html):
        return self.findbyre('(?s)geboren:[^<>]*te ([^<>]*)', html, 'city')

    def finddeathplace(self, html):
        return self.findbyre('(?s)overleden:[^<>]*te ([^<>]*)', html, 'city')

    def findsources(self, html):
        return self.findallbyre('(?s)<p class="bronnen">(.*?)<', html, 'source')

    def findtitles(self, html):
        section = self.findbyre('(?s)Adelstitel:(.*?)<', html)
        if section:
            return self.findallbyre('([a-zA-Z][\w\s]*)', section, 'title')

    def findpositions(self, html):
        result = []
        section = self.findbyre('(?s)Overige:(.*?)<', html)
        if section:
            result += self.findallbyre('([a-zA-Z][\w\s]*)', section, 'position')
        section = self.findbyre('(?s)<h2>functies.*?</h2>(.*?)<!-- End Body -->', html)
        if section:
            parts = self.findallbyre('(?s)functie:(.*?<br.*?)<br', section)
            parts = [self.TAGRE.sub(' ', part) for part in parts]
            parts = [part.replace('instelling:', '') for part in parts]
            result += [self.findbyre('(?s)(.*)', part, 'position') for part in parts]
        result += self.findallbyre('(?s)<span class="functie">(.*?)[\(<]', html, 'position')
        return result

    def findoccupations(self, html):
        result = []
        section = self.findbyre('(?s)Overige:(.*?)<', html)
        if section:
            result += self.findallbyre('([a-zA-Z][\w\s]*)', section, 'occupation')
        section = self.findbyre('(?s)<h2>functies.*?</h2>(.*?)<!-- End Body -->', html)
        if section:
            parts = self.findallbyre('(?s)functie:(.*?<br.*?)<br', section)
            parts = [self.TAGRE.sub(' ', part) for part in parts]
            parts = [part.replace('instelling:', '') for part in parts]
            result += [self.findbyre('(?s)(.*)', part, 'occupation') for part in parts]
        result += self.findallbyre('(?s)<span class="functie">(.*?)[\(<]', html, 'occupation')
        return result


class WikiAnalyzer(Analyzer):
    def setup(self):
        site = 'wikipedia'
        (self.language, self.id) = self.id.split(':', 1)
        if self.language in ['wikiquote', 'wikisource', 'wiktionary']:
            site = self.language
            (self.language, self.id) = self.id.split(':', 1)
        self.dbproperty = None
        if self.language == 'be-tarask':
            self.language = 'be-x-old'
        if self.language == 'nb':
            self.language = 'no'
        if site == 'wikipedia':
            self.dbid = {
                'nl': 'Q10000', 'bs': 'Q1047829', 'nap': 'Q1047851', 'vec': 'Q1055841', 'sc': 'Q1058430', 'ur': 'Q1067878',
                'ast': 'Q1071918', 'bg': 'Q11913', 'it': 'Q11920', 'pt': 'Q11921', 'sl': 'Q14380', 'pl': 'Q1551807',
                'id': 'Q155214', 'sv': 'Q169514', 'fi': 'Q175482', 'ja': 'Q177837', 'ko': 'Q17985', 'da': 'Q181163',
                'eo': 'Q190551', 'cs': 'Q191168', 'no': 'Q58691283', 'sk': 'Q192582', 'ca': 'Q199693', 'uk': 'Q199698',
                'ar': 'Q199700', 'ro': 'Q199864', 'he': 'Q199913', 'et': 'Q200060', 'vi': 'Q200180', 'sr': 'Q200386',
                'lt': 'Q202472', 'hr': 'Q203488', 'ru': 'Q206855', 'sq': 'Q208533', 'nn': 'Q2349453', 'zh': 'Q30239',
                'en': 'Q328', 'jv': 'Q3477935', 'km': 'Q3568044', 'mr': 'Q3486726', 'ps': 'Q3568054', 'bn': 'Q427715',
                'de': 'Q48183', 'fa': 'Q48952', 'hu': 'Q53464', 'th': 'Q565074', 'tr': 'Q58255', 'hi': 'Q722040',
                'lv': 'Q728945', 'ceb': 'Q837615', 'fr': 'Q8447', 'es': 'Q8449', 'te': 'Q848046', 'km': 'Q8565447',
                'sh': 'Q58679', 'af': 'Q766705', 'als': 'Q1211233', 'eu': 'Q207620', 'commons': 'Q565', 'species': 'Q13679',
                'fy': 'Q2602203', 'el': 'Q11918', 'mai': 'Q18508969', 'hy': 'Q1975217', 'ka': 'Q848974', 'li': 'Q2328409',
                'be': 'Q877583', 'be-x-old': 'Q8937989', 'gl': 'Q841208', 'xmf': 'Q2029239', 'bpy': 'Q1287192',
                'ta': 'Q844491', 'ml': 'Q874555', 'br': 'Q846871', 'zh-min-nan': 'Q3239456', 'oc': 'Q595628',
                'simple': 'Q200183', 'te': 'Q848046', 'az': 'Q58251', 'sco': 'Q1444686', 'nah': 'Q2744155',
                'pms': 'Q3046353', 'la': 'Q12237', 'azb': 'Q20789766', 'eu': 'Q207260', 'zh-classical': 'Q37041',
                'av': 'Q562665', 'ba': 'Q58209',  'ce': 'Q4783991', 'ms': 'Q845993', 'so': 'Q8572132',
                'vls': 'Q3568038', 'ckb': 'Q4115463', 'tl': 'Q877685', 'am': 'Q3025527', 'bo': 'Q2091593',
                'io': 'Q1154766', 'is': 'Q718394', 'sd': 'Q8571840', 'dv': 'Q928808', 'uz': 'Q2081526',
                'ug': 'Q60856', 'lb': 'Q950058', 'cy': 'Q848525', 'ky': 'Q60799', 'ku': 'Q1154741', 'kk': 'Q58172',
                'ga': 'Q875631', 'nds': 'Q4925786', 'ilo': 'Q8563685', 'mg': 'Q3123304', 'mk': 'Q842341',
                'pa': 'Q1754193', 'war': 'Q1648786', 'vo': 'Q714826', 'an': 'Q1147071',  'arz': 'Q2374285',
                'bcl': 'Q8561870', 'ht': 'Q1066461', 'qu': 'Q1377618', 'zh_min_nan': 'Q3239456', 'sw': 'Q722243',
                'nds-nl': 'Q1574617',
            }[self.language]
        elif site == 'wikisource':
            self.dbid = {
                'en': 'Q15156406', 'pl': 'Q15298974', 'ru': 'Q15634506', 'de': 'Q15522295', 'fr': 'Q15156541',
                'zh': 'Q19822573', 'he': 'Q22004676', 'it': 'Q15281537', 'es': 'Q15618752', 'ar': 'Q24577645',
                'nl': 'Q24577681', 'cs': 'Q16735590', 'la': 'Q21205461',
            }[self.language]
        else:
            self.dbid = {'wikiquote': 'Q369', 'wiktionary': 'Q151'}[site]
        self.iswiki = True
        self.skipfirst = True
        self.id = self.id.replace(' ', '_')
        if self.language in ['commons', 'species']:
            site = 'wikimedia'
        self.dbname = '{} {}'.format(site.title(), self.language.upper())
        self.urlbase = 'https://%s.%s.org/wiki/{id}'%(self.language, site)
        self.urlbase3 = 'https://%s.%s.org/w/index.php?title={id}&veswitched=1&action=edit'%(self.language, site)
        self.hrtre = '\{\{(.*?)\}\}'
        self.mainRE = '(?s)<textarea[^<>]*name="wpTextbox1">(.*?)</textarea>'
        self.escapehtml = True
        if self.language in ['commons', 'species', 'simple']:
            self.language = 'en'

    def prepare(self, html):
        def reworkwikilink(wikipart):
            parts = wikipart.group(1).split('|')
            return '[[{}]]'.format(parts[0] if ':' in parts[0] else parts[-1])

        if not html: return None
        f = codecs.open('result.html', 'w', 'utf-8')
        f.write(html)
        f.close()
        html = re.search(self.mainRE, html).group(1)
        html = re.sub('\{\{nowrap\|([^\{\}]*)\}\}', '\1', html)
        return re.sub('\[\[([^\[\]]*)\]\]', reworkwikilink, html)

    def excludetemplatelight(self, text):
        templatetype = re.search('([^\{\|]*)', text).group(0).lower().strip()
        firstword = templatetype.split()[0]
        lastword = templatetype.split()[-1]
        return templatetype in ['sourcetext', 'ref-llibre', 'article', 'lien web', 'مرجع ويب', 'écrit'] or\
               firstword in ['citeer', 'cite', 'link', 'cita', 'cytuj', 'книга', 'citar', 'ouvrage', 'grafikus', 'citation',
                             'erreferentzia', 'citace', 'lien'] or\
               lastword in ['source', 'स्रोत']

    def getinfos(self, names, html, dtype=None, splitters='<>,;/،・', alt=None):
        if not alt: alt = [] 
        if not splitters: splitters = None
        result = []
        for name in names:
            boxes = self.findallbyre('(?s)\{\{((?:\{\{[^\}]*\}\}|[^\{\}])*)\}\}', html.replace('[[', '').replace(']]', '').replace("'''", ""))
            for box in boxes:
                if self.excludetemplatelight(box):
                    continue
                if not splitters:
                    result += self.findallbyre('(?is)[\b\|_\s]%s\s*=([^\|、]+)'%name, box, dtype, alt=alt)
                else:
                    sections = self.findallbyre('(?is)[\b\|_\s]%s\s*=([^\|、]+)'%name, box, alt=alt)
                    for section in sections:
                        result += self.findallbyre('([^%s]+)'%splitters, section, dtype)
        return result

    def getinfo(self, names, html, dtype=None, splitters=None, alt=None):
        if not alt: alt=[]
        for name in names:
            boxes = self.findallbyre('(?s)\{\{((?:\{\{[^\}]*\}\}|[^\{\}])*)\}\}', html.replace('[[', '').replace(']]', '').replace("'''", ""))
            for box in boxes:
                if self.excludetemplatelight(box):
                    continue
                if not splitters:
                    result = self.findallbyre('(?is)[\b\|_\s]%s\s*=([^\|]+)'%name, box, dtype, alt=alt)
                else:
                    preresult = self.findallbyre('(?is)[\b\|_\s]%s\s*=([^\|]+)'%name, box, alt=alt)
                    for section in preresult:
                        result = self.findallbyre('([^%s]+)'%splitters, section, dtype)
                if result:
                    return result[0]

    def findnames(self, html):
        result = self.findallbyre("'''([^']+)'''", html.replace('[[', '').replace(']]', '').replace('{{nbsp}}', ' ').replace("'''", "").replace("''", ""))
        result += self.findallbyre('\{\{voir homonymes\|(.*?)\}', html)
        sections = self.getinfos(['[\w\s_]*n[ao]me[\w\s_]*', '[\w\s\_]*naam\d*', 'autre noms', '[\w\s_]*name[ns]', 'imię[\w\s]*', 'pseudonie?m',
                                  '[\w\s]*imiona', 'имя(?:[\s_][\w\s_])*', 'под именем(?:_\d+)?', '[\w\s]*име(?:-[\w\s]+)?', '人名', '全名', "ім'я(?:[\s_][\w\s_]*)?",
                                  'tên[\w\s]*', '名称', '[\w\s_]*імен[аі]', 'псевдонім', 'beter-bekend-als', 'nombre[\w\s]*', 'الاسم', 'jméno',
                                  '[\w\s_]*ime', 'nom(?:[\s_][\w\s_]+)?', '[\w\s]*vardas', 'ook bekend als', 'alias', 'otros nombres',
                                  '[\w\s]*שם[\w\s]*', '[\w\s]*név', 'ふりがな', '別名義', "ім'я[\w\s\_]*", 'псевдонім', 'прізвисько',
                                  'pseudônimos?', '[\w\s-]*όνομα', '[\w\s]*есімі', 'isim', '[\w\s_]*isimleri', 'adı', 'نام', 'لقب',
                                  '[\w\s]*imię[\w\s]*', 'alcume', '芸名', '本名', '\w*이름', '본명', 'anarana', 'ime', 'jina[\w\s]*',
                                  'nom de naissance', '\w*namen',
                                  ], html)
        for section in sections:
            result += self.findallbyre('([^,;]*)', section)
        return [
            self.id.replace('_', ' ').split('(')[0].split(':',1)[-1]] + result

    def findlanguagenames(self, html):
        values = self.findallbyre('\{\{lang[-\|](\w+\|.*?)\}\}', html.replace("'''", ""))
        result = [value.split('|', 1) for value in values]
        values = self.findallbyre('\[\[(\w\w:.+?)\]\]', html)
        result += [value.split(':', 1) for value in values]
        return result

    def excludetemplate(self, text):
        templatetype = re.search('([^\{\|]+)', text).group(0).lower().strip()
        firstword = templatetype.split()[0]
        lastword = templatetype.split()[-1]
        return templatetype in ['sourcetext', 's-bef', 's-ttl', 's-aft', 'appendix', 'familytree', 'ref-llibre',
                                'sfn', 'obra citada', 'arbre généalogique', 'infobox chinese namen', 'infobox tibetaanse namen',
                                'article', 'הערה', 'مرجع ويب', 'écrit'] or\
               firstword in ['citeer', 'cite', 'ouvrage', 'link', 'grafikus', 'cita', 'cytuj', 'книга', 'citar', 'ouvrage',
                             'citation', 'erreferentzia', 'lien', 'citace'] or\
               lastword in ['source', 'स्रोत'] or\
               templatetype.startswith('ahnentafel')

    def findlongtext(self, html):
        changedhtml = html.strip()
        while changedhtml.startswith('{{'):
            changedhtml = changedhtml[changedhtml.find('}}')+2:].strip()
        return changedhtml[:2000] + "\n---\n" + "\n".join([x for x in self.findallbyre('(?s)\{\{((?:[^\{\}]|\{\{[^\}]*\}\})*=(?:[^\{\}]|\{\{[^\}]*\}\})*)\}\}', html) if not self.excludetemplate(x)]) + "\n" + " - ".join(self.findallbyre('\[\[(\w+:.*?)\]\]', html))

    def removewiki(self, text):
        if not text:
            return None
        return text.replace('[[', '').replace(']]', '').replace("'''", "").replace("''", "")

    def finddescriptions(self, html):
        return self.getinfos(['fineincipit', 'commentaire', 'kurzbeschreibung', 'fets_destacables', 'описание', 'bekendvan',
                              'postcognome', 'postnazionalità', 'known_for', 'description', 'başlık'], html) +\
               [self.removewiki(self.findbyre(" %s (?:e[ei]?n |an? |u[nm][ea]? |eine[nr]? |'n |ne |e )?(.*?)[\.;]"%word, html)) for word in [
                'is', 'w[ao]s', 'ist', 'wao?r', 'est', 'était', 'fu', 'fou', '—', 'era', 'е', 'היה', 'by[łl]', 'foi', 'был', 'fue',
                   'oli', 'bio' , 'wie', 'var', 'je', 'იყო', 'adalah', 'é', 'ήταν', 'هو', 'стала', 'és', 'er', 'est[ia]s',
                   'एक',
               ]] +\
               self.findallbyre('\{\{short description\|(.*?)\}', html) +\
               self.findallbyre('\[\[[^\[\]\|]+?:([^\[\]\|]+)\]\]', html) +\
               [x.replace('_', ' ') for x in  self.findallbyre('\((.*?)\)', self.id)]

    def findoccupations(self, html):
        return self.getinfos(['charte', 'attività\s*(?:altre)?\d*', 'occupation', 'zawód', 'functie', 'spfunc', 'beroep',
                              'рід_діяльності', 'المهنة', 'ocupación', 'עיסוק', '職業', 'ocupação', 'ιδιότητα', 'мамандығы',
                              'zanimanje', 'meslek', 'mesleği', 'activités?', 'پیشه', 'профессия', 'profesión', '직업',
                              'asa', 'kazi yake', '(?:antaŭ|aliaj)?okupoj?\d*',
                              ], html, 'occupation') +\
               self.findallbyre('(?i)info(?:box|boks|taula)([\w\s]+)', html, 'occupation') + self.findallbyre('基礎情報([\w\s]+)', html, 'occupation') +\
               self.findallbyre('\{([\w\s]+)infobox', html, 'occupation') + self.findallbyre('Categorie:\s*(\w+) (?:van|der) ', html, 'occupation') +\
               self.findallbyre('(?i)inligtingskas([\w\s]+)', html, 'occupation')

    def findpositions(self, html):
        return self.getinfos(['functie\d?', 'titre\d', 'stanowiko', '(?:\d+\. )?funkcja', 'должность(?:_\d+)?', 'títulos?\d*',
                              'tytuł', 'titles', 'chức vị', 'amt\d*', 'jabatan', 'carica', '(?:altri)?titol[oi]', 'титул_?\d*',
                              'anderwerk', 'titels', 'autres fonctions', 'апісанне выявы', 'titul(?:y|as)?\d*', 'title',
                              '\w*ambt(?:en)?', 'carica', 'other_post', 'посада', '事務所'], html, 'position') +\
            self.findallbyre('S-ttl\|title\s*=(.*?)\|', html, 'position') + self.findallbyre("Categor[ií]a:((?:Re[iy]e?|Conde)s d['e].*?)(?:\]|del siglo)", html, 'position') +\
            self.findallbyre('Kategorie:\s*(König \([^\[\]]*\))', html, 'position') + self.findallbyre("Category:([^\[\]]+ king)", html, 'position') +\
            self.findallbyre('Catégorie:\s*(Roi .*?)\]', html, 'position') + self.findallbyre("Kategoria:(Królowie .*?)\]", html, 'position') +\
            self.findallbyre('Kategori:(Raja .*?)\]', html, 'position') + self.findallbyre('[cC]ategorie:\s*((?:Heerser|Bisschop|Grootmeester|Abdis|Koning|Drost) .*?)\]', html, 'position')

    def findtitles(self, html):
        return self.getinfos(['titre\d*', 'титул_?\d*', 'tước vị[\w\s]*', '爵位', 'titels', 'titles', 'títuloas', 'titul(?:y|as|ai)?\d*',
                              '(?:altri)?titol[oi]',], html, 'title') +\
               self.findallbyre('Categorie:\s*((?:Heer|Vorst|Graaf) van.*?)\]', html, 'title') + self.findallbyre('Kategorie:\s*((?:Herzog|Herr|Graf|Vizegraf) \([^\[\]]*\))\s*\]', html, 'title') +\
               self.findallbyre('Catégorie:\s*((?:Duc|Prince|Comte) de.*?)\]', html, 'title') +\
               self.findallbyre('Category:((?:Du(?:k|chess)e|Princ(?:ess)?e|Lord|Margrav(?:in)?e|Grand Master|Count|Viscount)s of.*?)\]', html, 'title') +\
               self.findallbyre('Categoría:((?:Prínciple|Señore|Conde|Duque)s de .*?)\]', html, 'title') + self.findallbyre('Kategória:([^\[\]]+ királyai)', html, 'title')

    def findspouses(self, html):
        return self.getinfos(['spouse', 'consorte', 'conjoint', 'małżeństwo', 'mąż', 'супруга', 'съпруга на', '[\w\s]*брак',
                              'echtgenoot', 'echtgenote', '配偶者\d*', '(?:\d+\. )?związek(?: z)?', 'чоловік', 'phối ngẫu',
                              'vợ', 'chồng', 'الزوج', 'жонка', 'královna', 'sutuoktin(?:ė|is)', 'partners?', 'supružnik',
                              'gade', 'cónyuge', 'conjoint', 'házastárs', 'дружина', 'cônjuge', 'σύζυγος', 'همسر',
                              'współmałżonek', 'c[ôo]njuge', 'cónxuxe', '배우자', 'ndoa',
                             ], html, 'person', splitters = '<>,;)') +\
                             self.findallbyre('\{(?:marriage|matrimonio)\|(.*?)[\|\}]', html, 'person')

    def findpartners(self, html):
        return self.getinfos(['liaisons', 'partner\d*', 'partnerka', 'relacja', 'cónyuge', 'فرزندان', 'lewensmaat',
                              ], html, 'person')

    def findfather(self, html):
        return self.getinfo(['father', 'padre', 'vader', 'père', 'far', 'ojciec', 'отец', 'баща', '父親', 'батько', 'cha',
                             'الأب', 'per', 'бацька', 'pai', 'otec', 'tėvas', 'батько', 'nome_pai'], html, 'person') or\
               self.getinfo(['rodzice', 'parents', 'roditelji', 'γονείς', 'والدین', 'parella', '부모', 'wazazi', 'ouers',
                             ], html, 'male-person') or\
               self.findbyre('\|otec\|([^\|\{\}]*)\}', html, 'person')

    def findmother(self, html):
        return self.getinfo(['mother', 'madre', 'moeder', 'mère', 'mor', 'matka', 'мать', 'майка', '母親', 'матір', 'mẹ',
                             'الأم', 'mer', 'маці', 'mãe', 'motina', 'мати', 'nome_mãe',], html, 'person') or\
               self.getinfo(['rodzice', 'parents', 'roditelji', 'γονείς', 'والدین', 'parella', '부모', 'wazazi', 'ouers',
                             ], html, 'female-person') or\
               self.findbyre('\|matka\|([^\|\{\}]*)\}', html, 'person')

    def findchildren(self, html):
        return self.getinfos(['issue', 'figli', 'enfants', 'children', 'kinder(?:en|s)', '(?:\d+\. )?dzieci', 'дети', 'потомство',
                              '子女', 'діти', 'con cái', 'descendencia', 'الأولاد', 'potostvo', 'vaikai', 'hijos', 'enfant',
                              'fil[hl]os', 'діти', 'τέκνα', 'deca', 'çocukları', 'والدین', '자녀', 'watoto',
                              ], html, 'person')

    def findsiblings(self, html):
        return self.getinfos(['broerzus', 'rodzeństwo', 'rodbina', 'broer', 'zuster', 'αδέλφια', '형제자매',
                              ], html, 'person') +\
               self.findallbyre('\|(?:bratr|sestra)\|([^\|\{\}]*)\}', html, 'person') +\
               self.findallbyre('\[\[([^\[\]]*)\]\] \(brat\)', html, 'person')

    def findkins(self, html):
        return self.getinfos(['родичі', 'famille', '著名な家族', '친척'], html, 'person')

    def findfamily(self, html):
        return self.getinfo(['house', 'd[iy]nast[iyí]j?[ae]?', 'famille', 'noble family', 'rodzina', 'род', 'династия',
                             '王家', '王朝', 'hoàng tộc', 'casa', '家名・爵位', 'рід'], html, 'family') or\
               self.findbyre('Categorie:\s*Huis(.*?)\]\]', html, 'family') or self.findbyre('Catégorie:\s*Maison (.*?)\]\]', html, 'family') or\
               self.findbyre('Category:([^\[\]]*)(?:dynasty|family)', html, 'family') or self.findbyre('Kategorie:\s*Haus(.*?)\]', html, 'family') or\
               self.findbyre('Categor[ií]a:Casa(?:to)? d[ei](.*?)\]', html, 'family') or self.findbyre('Kategory:Hûs(.*?)\]', html, 'family') or\
               self.findbyre('Categorie:\s*([^\[\]]*)dynastie\]', html, 'family') or self.findbyre('Category:House of(.*?)\]', html, 'family')

    def findgens(self, html):
        return self.findbyre('Categorie:\s*Gens(.*?)\]\]', html, 'gens')

    def findbirthdate(self, html):
        return self.findbyre('\{\{(?:[bB]irth date(?: and age)?|dni|[dD]oğum tarihi ve yaşı|출생일|geboortedatum en ouderdom)\|(\d+\|\d+\|\d+)', html) or\
               self.getinfo(['geburtsdatum', 'birth[_ ]?date', 'data di nascita', 'annonascita', 'geboren?', 'født', 'data urodzenia',
                             'data_naixement', 'gbdat', 'data_nascimento', 'дата рождения', '出生日', 'дата_народження',
                             'geboortedatum', 'sinh', 'fecha de nacimiento', 'تاريخ الولادة', 'date de naissance', 'дата нараджэння',
                             'data de nascimento', 'datum narození', 'gimė', 'תאריך לידה', 'születési dátum', 'дата народження',
                             'jaiotza data', 'nascimento_data', 'ημερομηνία γέννησης', 'туған күні', 'datum_rođenja', 'تاریخ تولد',
                             'teraka', 'alizaliwa', 'naskiĝjaro',
                             ], html) or\
               self.findbyre('Category:\s*(\d+) births', html) or self.findbyre('Kategorie:\s*Geboren (\d+)', html) or\
               self.findbyre('Catégorie:\s*Naissance en ([^\[\]]*)\]', html) or self.findbyre('Categorie:\s*Nașteri în (.*?)\]', html) or\
               self.findbyre('(.*)-', self.getinfo(['leven'], html) or '') or self.findbyre('Kategory:Persoan berne yn(.*?)\]', html) or\
               self.findbyre('\{\{bd\|([^\{\}]*?)\|', html) or self.findbyre('(\d+)年生', html)

    def finddeathdate(self, html):
        return self.findbyre('\{\{(?:[dD]eath date[\w\s]*|morte|사망일과 나이)\|(\d+\|\d+\|\d+)[\}\|]', html) or\
               self.getinfo(['sterbedatum', 'death[_ ]?date', 'data di morte', 'annomorte', 'date de décès', 'gestorven', 'død',
                             'data śmierci', 'data_defuncio', 'sterf(?:te)?dat\w*', 'data_morte', 'дата смерти', '死亡日', 'дата_смерті',
                             'mất', 'overlijdensdatum', 'overleden', 'fecha de defunción', 'تاريخ الوفاة', 'datum_smrti',
                             'дата смерці', 'dta da morte', 'datum úmrtí', 'mirė', 'oorlede', 'fecha de fallecimiento',
                             'תאריך פטירה', 'halál dátuma', 'дата смерті', 'heriotza data', 'morte_data', 'ημερομηνία θανάτου',
                             'қайтыс болған күн7і', 'datum_smrti', 'ölüm_tarihi', 'تاریخ مرگ', 'falecimento', 'maty', 'alikufa',
                             'mortjaro',
                             ], html) or\
               self.findbyre('Category:\s*(\d+) deaths', html) or self.findbyre('Catégorie:\s*Décès en ([^\[\]]*)\]', html) or\
               self.findbyre('Kategorie:\s*Gestorben (\d+)', html) or self.findbyre('\{\{death year and age\|(.*?)\|', html) or\
               self.findbyre('Categoria:Mortos em (.*?)\]', html) or self.findbyre('Category:(\d+)年没\]', html) or\
               self.findbyre('Categorie:\s*Decese în (.*?)\]', html) or self.findbyre('Kategori:Kematian(.*?)\]', html) or\
               self.findbyre('Kategory:Persoan stoarn yn (.*?)\]', html) or\
               self.findbyre('-(.*)', self.getinfo(['leven'], html) or '') or self.findbyre('(\d+)年没', html) or\
               self.findbyre('\{\{bd\|[^[\|\{\}]*\|[^[\|\{\}]*\|([^[\|\{\}]*)\|', html)

    def findburialdate(self, html):
        return self.getinfo(['埋葬日', 'datum pohřbení'], html)
    
    def findbirthplace(self, html):
        return self.getinfo(['birth[_ ]?place', 'luogo di nascita', 'luogonascita\w*', 'geboren_in', 'geburtsort', 'fødested', 'geboorteplaats',
                             'miejsce urodzenia', 'lloc_naixement', 'gbplaats', 'место рождения', 'място на раждане', '生地',
                             'місце_народження', 'lugar\s*de\s*nac[ei]mi?ento', 'مكان الولادة', 'lieu de naissance', 'месца нараджэння',
                             'local de nascimento', 'místo narození', 'gimimo vieta', 'geboortestad', 'geboorteplek', 'תאריך לידה',
                             'születési hely', '出生地', 'місце народження', 'nascimento_local', 'τόπος γέννησης', 'туған жері',
                             'mj?esto_rođenja', 'doğum_yeri', 'محل تولد', 'local_nascimento', 'роден-място', '출생지',
                             'naskiĝloko',
                             ], html, 'city') or\
               self.findbyre('Category:Births in(.*?)\]', html, 'city')

    def finddeathplace(self, html):
        return self.getinfo(['death[_ ]?place', 'luogo di morte', 'luogomorte', 'lieu de décès', 'gestorven_in', 'sterbeort',
                             'dødested', 'miejsce śmierci', 'lloc_defuncio', 'sterfplaats', 'место смерти', 'място на смъртта',
                             '没地', 'місце_смерті', 'nơi mất', 'overlijdensplaats', 'lugar de defunción', 'مكان الوفاة',
                             'месца смерці', 'local da morte', 'místo úmrtí', 'mirties vieta', 'stadvanoverlijden', 'מקום פטירה',
                             'sterfteplek', 'lugar de fallecimiento', 'halál helye', '死没地', 'місце смерті', 'morte_local',
                             'τόπος θανάτου', 'қайтыс болған жері', 'mj?esto_smrti', 'ölüm_yeri', 'محل مرگ', 'починал-място',
                             'lugardefalecemento', '사망지', 'mortloko',
                             ], html, 'city') or\
               self.findbyre('\{\{МестоСмерти\|([^\{\}\|]*)', html, 'city') or\
               self.findbyre('Category:Deaths in(.*?)\]', html, 'city')

    def findburialplace(self, html):
        return self.getinfo(['place of burial', 'sepoltura', 'begraven', 'gravsted', 'resting_place', 'miejsce spoczynku', 'sepultura',
                             'похоронен', 'погребан', '埋葬地', '陵墓', 'burial_place', 'lugar de entierro', 'مكان الدفن',
                             'local de enterro', 'místo pohřbení', 'palaidotas', 'поховання', 'مدفن'], html, 'cemetery', alt=['city']) or\
               self.findbyre('Category:Burials at (.*?)\]', html, 'cemetery')

    def findreligions(self, html):
        return self.getinfos(['religione?', '宗教', 'wyznanie', 'religij?[ea]', 'الديانة', 'церковь_?\d*', 'church',
                              'конфесія', 'religião', '종교',
                              ], html, 'religion') +\
            self.findallbyre('Catégorie:Religieux(.*?)\]', html, 'religion')

    def findnationalities(self, html):
        return self.getinfos(['nazionalità[\w\s_]*', 'allégeance', 'land', 'nationality', 'narodowość', 'państwo', 'громадянство',
                              'нац[іи]ональ?н[іо]сть?', 'الجنسية', 'nacionalnost', 'nationalité', 'na[ts]ionaliteit', 'citizenship',
                              'geboorteland', 'nacionalidade?', 'מדינה', '国籍', 'підданство', 'εθνικότητα', 'υπηκοότητα',
                              'nazione\d*', 'азаматтығы', 'ملیت', 'гражданство', 'nacionalitat', 'firenena', 'nchi',
                              'nationalteam\d*', 'ŝtato',
                              ], html, 'country') or\
               self.findallbyre('Category:\d+th-century people of (.*?)\]\]', html, 'country') or\
               self.findallbyre('Categorie:\s*Persoon in([^\[\]]+)in de \d+e eeuw', html, 'country') or\
               self.findallbyre('Category:\d+th-century ([^\[\]]+) people\]\]', html, 'country') or\
               self.findallbyre('Category:([^\[\]]+) do século [IVX]+\]\]', html, 'country') or\
               self.findallbyre('Kategorie:\s*Person \(([^\[\]]*)\)\]', html, 'country') or\
               self.findallbyre('Kategori:Tokoh(.*?)\]', html, 'country') or\
               self.findallbyre('Categoria:([^\[\]]+) del Segle [IVX]+', html, 'country') or\
               self.findallbyre('Categorie:\s*([^\[\]]*) persoon\]', html, 'country')

    def findlastname(self, html):
        return self.getinfo(['cognome', 'surnom', 'familinomo'], html, 'lastname') or\
               self.findbyre('(?:DEFAULTSORT|SORTIERUNG):([^\{\},]+),', html, 'lastname')

    def findfirstname(self, html):
        return self.getinfo(['antaŭnomo'], html, 'firstname') or\
               self.findbyre('(?:DEFAULTSORT|SORTIERUNG|ORDENA):[^\{\},]+,\s*(\w+)', html, 'firstname')

    def findgender(self, html):
        return self.getinfo(['sesso'], html, 'gender') or self.findbyre('Kategorie:\s*(Mann|Frau|Kvinnor)\]', html, 'gender')

    def findmemberships(self, html):
        return self.getinfos(['org', 'groep'], html, 'organization') +\
               self.getinfos(['associated_acts', 'artistas_relacionados'], html, 'group') +\
               self.findallbyre('Categor(?:ie|y):\s*(?:Lid van|Members of)(.*?)\]\]', html, 'organization')

    def findmixedrefs(self, html):
        imdb = self.findbyre('IMDb name\|([^\{\}]*)\|', html) or self.getinfo(['imdb', 'imdb_id'], html)
        if imdb and imdb.strip() and imdb.strip()[0] in '0123456789':
            imdb = 'nm' + imdb.strip()
        if not imdb or not imdb.strip() or imdb.startswith('tt'):
            imdb = None
        return self.finddefaultmixedrefs(html) + [
            ('P214', self.getinfo(['viaf'], html)),
            ('P227', self.getinfo(['gnd'], html)),
            ('P345', imdb),
            ('P349', self.getinfo(['ndl'], html)),
            ('P723', self.getinfo(['dbnl'], html)),
            ('P1220', self.getinfo(['ibdb'], html)),
            ('P1969', self.getinfo(['moviemeter'], html)),
            ('P2002', self.getinfo(['twitter'], html)),
            ('P2013', self.getinfo(['facebook'], html)),
        ]

    def findschools(self, html):
        return self.getinfos(['education', 'alma[ _]m[aá]ter', 'edukacja', 'uczelnia', 'formation', 'skool',
                              'universiteit',
                              ], html, 'university') +\
               self.findallbyre('Kategorie:\s*Absolvent de[rs] (.*?)\]', html, 'university') +\
               self.findallbyre('Category:\s*Alumni of(?: the)?(.*?)\]', html, 'university') +\
               self.findallbyre('Category:People educated at(.*?)\]', html, 'university') +\
               self.findallbyre('Category:([^\[\]]+) alumni\]', html, 'university')

    def findemployers(self, html):
        return self.getinfos(['employer', 'pracodawca', 'work_institutions', 'empleador'], html, 'employer', alt=['university'])

    def findteachers(self, html):
        return self.getinfos(['maîtres?', 'leraren'], html, 'artist')

    def findwebsite(self, html):
        result = self.getinfo(['website', 'www', 'site internet', 'אתר אינטרנט', 'honlap', '公式サイト',
                               'сайты?', 'ιστοσελίδα', 'sitio web', 'وب‌گاه', 'web', '웹사이트',
                               'tovuti rasmi', 'webwerf',
                               ], html)
        if result:
            return self.findbyre('(\w+://[\w/\.\-_]+)', result)

    def findwebpages(self, html):
        return self.getinfos(['קישור'], html)

    def findmannerdeath(self, html):
        return self.getinfo(['przyczyna śmierci', 'причина_смерті', 'سبب الوفاة', 'doodsoorzaak', 'death_cause',
                             'причина смерті'], html, 'mannerdeath') or\
               self.findbyre('Categoría:Fallecidos por(.*?)\]', html, 'mannerdeath')

    def findcausedeath(self, html):
        return self.getinfo(['przyczyna śmierci', 'причина_смерті', 'سبب الوفاة', 'doodsoorzaak', 'death_cause',
                             'причина смерті'], html, 'causedeath') or\
               self.findbyre('Categoría:Fallecidos por(.*?)\]', html, 'causedeath')

    def findresidences(self, html):
        return self.getinfos(['miejsce zamieszkania', 'місце_проживання', 'الإقامة', 'residence', 'residência',
                              'місце проживання'], html, 'city')

    def finddegrees(self, html):
        return self.getinfos(['tytuł naukowy', 'education'], html, 'degree')

    def findheight(self, html):
        return self.getinfo(['зріст', 'estatura', '身長', 'зріст', '身長', 'height'], html)

    def findweights(self, html):
        return self.getinfos(['masa', 'вага', 'вага'], html, splitters=None)

    def findparties(self, html):
        return self.getinfos(['partia', 'партія'], html, 'party')

    def findawards(self, html):
        return self.getinfos(['odznaczenia', 'onderscheidingen', 'الجوائز', 'distinctions', 'prizes',
                              'pr[eé]mios[\w\s]*', 'ou?tros premios', 'awards', 'нагороди', 'марапаттары',
                              'apdovanojimai', 'جوایز', 'nagrody', '수상', 'toekennings',
                              ], html, 'award')

    def findranks(self, html):
        return self.getinfos(['rang', 'grade militaire', 'військове звання'], html, 'rank')

    def findimage(self, html):
        result = self.getinfo(['image[nm]?', 'immagine', 'изображение(?: за личността)?', '画像', 'grafika',
                               'afbeelding', 'hình', '圖像', 'зображення', 'afbeelding', 'صورة', 'выява',
                               'obrázek', 'vaizdas', 'slika', 'beeld', 'kép', '画像ファイル', 'зображення',
                               'εικόνα', 'сурет', 'foto', 'slika', 'resim', 'تصویر', 'награды', 'портрет',
                               'imaxe', '사진', 'sary', 'picha', 'dosiero',
                               ], html)
        if result and '.' in result:
            return result.split(':')[-1]

    def findcoatarms(self, html):
        return self.getinfo(['герб', 'herb', 'escudo', 'icone', 'пасада', 'герб'], html)

    def findsignature(self, html):
        return self.getinfo(['подпис', 'faksymile', 'توقيع', 'po[dt]pis', 'handtekening', 'автограф',
                             'підпис', 'imza', 'sinatura',
                             ], html)

    def findbranches(self, html):
        return self.getinfos(['onderdeel', 'eenheid', 'arme'], html, 'militarybranch')

    def findconflicts(self, html):
        return self.getinfos(['veldslagen(?:-naam)?', 'conflic?ts'], html, 'conflict')

    def findinworks(self, html):
        return self.findallbyre('Category:Characters in(.*?)\]', html, 'work') +\
               self.findallbyre('Categor[ií]a:Persona[tg]?[jg][ei]n?s? d[eo][li]?(.*?)\]', html, 'work') +\
               self.findallbyre('Kategorie:\s*Person i[nm](.*?)\]', html, 'work') +\
               self.findallbyre('Category:People in(.*?)\]', html, 'work') +\
               self.findallbyre('Catégorie:\s*Personnage d[ue]s?(.*?)\]', html, 'work') +\
               self.findallbyre('Categorie:\s*Persoon uit(.*?)\]', html, 'work')

    def findethnicities(self, html):
        return self.getinfos(['عرقية', 'ethnicity'], html, 'ethnicity')

    def findbloodtype(self, html):
        return self.getinfo(['血液型'], html, 'bloodtype')

    def findfeastday(self, html):
        return self.getinfo(['fête', 'feestdag', 'feast_day', 'festivi[dt]ad'], html, 'date')

    def findpatronof(self, html):
        return self.getinfos(['beschermheilige_voor', 'patronat?ge', 'patrono'], html, 'subject')

    def findrelorder(self, html):
        return self.getinfo(['ordre'], html, 'religious order')

    def findgenres(self, html):
        return self.getinfos(['stijl', 'gene?re\d*', 'estilo', 'ジャンル',], html, 'genre')

    def findmovements(self, html):
        return self.getinfos(['stroming', 'mou?vement', 'style', 'school_tradition', 'movimento', 'stijl',
                              ], html, 'movement')

    def findnotableworks(self, html):
        return self.getinfos(['notable\s?works?', 'bekende-werken', '\w+ notables', '主な作品',
                              'œuvres principales', 'principais_trabalhos', 'bitna uloga', 'obra-prima',
                              ], html, 'work') +\
               self.getinfos(['films notables', 'значими филми', 'millors_films', 'znameniti_filmovi',
                              'noemenswaardige rolprente',
                              ], html, 'film', alt=['work'])

    def findworkfields(self, html):
        return self.getinfos(['field', '(?:main_)?interests', 'known_for', 'زمینه فعالیت'], html, 'subject')

    def finddocstudents(self, html):
        return self.getinfos(['doctoral_students'], html, 'scientist')

    def findadvisors(self, html):
        return self.getinfos(['doctoral_advisor'], html, 'scientist')

    def findheights(self, html):
        return self.getinfos(['lengte', 'height'], html, splitters=None)

    def findsportteams(self, html):
        return self.getinfos(['clubs?\d*'], html, 'club')

    def findteampositions(self, html):
        return self.getinfos(['positie'], html, 'sportposition')

    def findlanguagesspoken(self, html):
        return self.getinfos(['שפה מועדפת', 'langue'], html, 'language')

    def findinfluences(self, html):
        return self.getinfos(['influences', 'influências', 'influence de', 'invloeden'], html, 'person')

    def findpseudonyms(self, html):
        return self.getinfos(['псевдонім', 'pseudonie?m', 'psudônimos?'], html)

    def findinstruments(self, html):
        return self.getinfos(['instrumento?', 'strumento'], html, 'instrument')

    def findlabels(self, html):
        return self.getinfos(['label', 'etichetta'], html, 'label')
    
    def findstudents(self, html):
        return self.getinfos(['leerlingen'], html, 'person')

    def findformationlocation(self, html):
        return self.getinfo(['origin'], html, 'city')

    def findparts(self, html):
        return self.getinfos(['members'], html, 'musician')


class UrlAnalyzer(Analyzer):
    def __init__(self, id, data=defaultdict(dict), item=None):
        super().__init__(id.split('/',3)[-1], data, item)
        self.urlbase = id
        self.dbproperty = None
        self.isurl = True


class DeutscheBiographieAnalyzer(UrlAnalyzer):
    def setup(self):
        self.dbid = 'Q1202222'
        self.dbname = 'Deutsche Biographie'
        self.hrtre = '<!-- Content -->(.*?)<h\d'
        self.language = 'de'

    def getvalue(self, field, html, dtype=None):
        return self.findbyre('(?s)<dt class="indexlabel">%s</dt>\s*<dd class="indexvalue">(.*?)</dd>'%field, html, dtype)

    def findnames(self, html):
        section = self.getvalue('Namensvarianten', html) or ''
        return self.findallbyre('<h1[^<>]*>(.*?)<', html) +\
               self.findallbyre('<li[^<>]*>(.*?)<', section)

    def findmixedrefs(self, html):
        return self.finddefaultmixedrefs(html, includesocial=False)

    def findbirthdate(self, html):
        section = self.getvalue('Lebensdaten', html)
        if section:
            return self.findbyre('(.*?\d+)', section)

    def finddeathdate(self, html):
        section = self.getvalue('Lebensdaten', html)
        if section:
            return self.findbyre('bis (.*)', section)

    def findoccupations(self, html):
        section = self.getvalue('Beruf/Funktion', html)
        if section:
            subsections = self.findallbyre('>([^<>]*)</a>', section)
            result = []
            for subsection in subsections:
                result += self.findallbyre('([^,]*)', subsection, 'occupation')
            return result

    def findreligions(self, html):
        section = self.getvalue('Konfession', html)
        if section:
            return self.findallbyre('([^,]+)', section, 'religion')


class BrooklynMuseumAnalyzer(UrlAnalyzer):
    def setup(self):
        self.dbid = None
        self.dbname = 'Brooklyn Museum'
        self.hrtre = '<div class="container artist oc-search-results">(.*?)<div class="container '
        self.language = 'en'

    def findnames(self, html):
        return self.findallbyre('<strong>(.*?)</strong>', html)

    def findlongtext(self, html):
        return self.findbyre('(?s)<div class="container artist oc-search-results">(.*?)<div class="container ', html)

    def findnationality(self, html):
        return self.findbyre('(?s)</strong>[^<>]*&ndash;([^<>]*?),', html, 'country')

    def findbirthdate(self, html):
        return self.findbyre('(?s)</strong>[^<>]*,([^<>,]*)-', html)

    def finddeathdate(self, html):
        return self.findbyre('(?s)</strong>[^<>]*-([^<>,\-]*)</div>', html)

    def findincollections(self, html):
        return ['Q632682']

class KunstaspekteAnalyzer(UrlAnalyzer):
    def setup(self):
        self.dbid = None
        self.dbname = 'KunstAspekte'
        self.hrtre = '<div class="artist-profile">(.*?)<div class="artist-data">'
        if not self.id.startswith('person/'):
            self.urlbase = None
        self.language = 'de'

    def description(self, html):
        return self.findbyre('(?s)"description": "(.*?)"', html) or\
            self.findbyre('(?s)<h3>short biography</h3>(.*?)</div>', html)

    def findlongtext(self, html):
        return self.description(html)

    def findnames(self, html):
        return [self.findbyre('(?s)"name": "(.*?)"', html)]

    def finddescriptions(self, html):
        section = self.description(html)
        if section:
            return section.split('\n')

    def findbirthdate(self, html):
        section = self.description(html)
        if section:
            return self.findbyre('\*\s*(\d+)', section)

    def findbirthplace(self, html):
        section = self.description(html)
        if section:
            return self.findbyre('\*\s*\d+(?: in)? ([^-!]*)', section.replace('\n', '!'), 'city')

    def findincollections(self, html):
        section = self.findbyre('(?s)<h3>collection/s</h3>(.*?)</div>', html)
        if section:
            return self.findallbyre('">(.*?)<', section, 'museum')


class NationalTrustAnalyzer(UrlAnalyzer):
    def setup(self):
        self.dbid = None
        self.dbname = 'National Trust Collections'
        self.hrtre = '<div class="sortable-header">(.*?)<h3'
        self.language = 'en'
        self.escapehtml = True

    def finddatesection(self, html):
        return self.findbyre('<b>[^<>]*\(([^<>]*\))', html)

    def findnames(self, html):
        return self.findallbyre('<b>(.*?)[<\(]', html)

    def finddescriptions(self, html):
        return self.findallbyre('<b>([^<>]*)</b>', html)

    def findbirthplace(self, html):
        section = self.finddatesection(html)
        if section:
            return self.findbyre('^([\w\s]*?) [\-\d]', section, 'city')

    def findbirthdate(self, html):
        section = self.finddatesection(html)
        if section:
            return self.findbyre(' (\d*) -', section)

    def finddeathplace(self, html):
        section = self.finddatesection(html)
        if section:
            return self.findbyre(' - ([\w\s]*?)(?: \d|\))', section, 'city')

    def finddeathdate(self, html):
        section = self.finddatesection(html)
        if section:
            return self.findbyre(' (\d*)\s*\)', section)

    def findincollections(self, html):
        return self.findallbyre('(?s)<label for="[^<>"]+">([^<>]*)</label>\s*<span class="item-bubble">[1-9]', html, 'museum')


class BenezitUrlAnalyzer(UrlAnalyzer):
    def setup(self):
        self.dbid = 'Q2929945'
        self.dbname = 'Benezit (url)'
        self.hrtre = '<h3>Extract</h3>(.*?)</div>'
        self.language = 'en'

    def findinstanceof(self, html):
        return 'Q5'

    def finddescription(self, html):
        return self.findbyre('"pf:contentName"\s*:\s*"(.*?)"', html)

    def findnames(self, html):
        return [self.findbyre('"pf:contentName"\s*:\s*"(.*?)[\("]', html)]

    def findlongtext(self, html):
        return self.findbyre('<abstract>(.*?)</abstract>', html)

    def findisntanceof(self, html):
        return "Q5"

    def findbirthdate(self, html):
        return self.findbyre('(?s)[^\w][bB]orn\s*((\w+\s*){,2}\d{4})[,\.\)]', html)

    def finddeathdate(self, html):
        return self.findbyre('(?s)[^\w][dD]ied\s*((\w+\s*){,2}\d{4})[,\.\)]', html)

    def findbirthplace(self, html):
        return self.findbyre('[bB]orn(?: [^<>,\.;]*,)? in ([^<>,\.;]*)', html, 'city')

    def finddeathplace(self, html):
        return self.findbyre('[dD]ied(?: [^<>,\.]*,)? in ([^<>,\.;]*)', html, 'city')

    def findoccupations(self, html):
        result = []
        section = self.findbyre('"pf:contentName" : "[^"]+-(.*?)"', html)
        if section:
            result += self.findallbyre('([^,]+)', section, 'occupation')
        section = self.findbyre('"pf:contentName" : "[^"]*\)(.*?)"', html)
        if section:
            result += self.findallbyre('([\s\w]+)', section, 'occupation')
        return result

    def findlastname(self, html):
        section = self.findbyre('"pf:contentName" : "([^"]+?),', html, 'lastname')

    def findfirstname(self, html):
        section = self.findbyre('"pf:contentName" : "[^",]+,\s*(\w+)', html, 'firstname')

    def findnationality(self, html):
        return self.findbyre('<abstract><p>([^<>]*?),', html, 'country')

    def findgender(self, html):
        return self.findbyre('<abstract><p>[^<>]*,([^<>,]*)\.</p>', html, 'gender')        
    

class UnivieAnalyzer(UrlAnalyzer):
    def setup(self):
        self.dbid = 'Q85217215'
        self.dbname = 'Database of Modern Exhibitions'
        self.hrtre = '<div class="lefthalf">(.*?)<div class="maphalf">'
        self.language = 'en'

    def getvalue(self, field, html, dtype=None):
        return self.findbyre('<meta property=(?:\w+:)?%s" content="(.*?)"'%field, html, dtype)

    def findinstanceof(self, html):
        return self.findbyre('"@type":"(.*?)"', html, 'instanceof')

    def finddescriptions(self, html):
        return [
            self.getvalue('description', html),
            self.findbyre('"description":"(.*?)"', html)
            ]

    def findnames(self, html):
        return [
            self.getvalue('title', html),
            self.findbyre('"name":"(.*?)"', html)
            ]

    def findfirstname(self, html):
        return self.getvalue('first_name', html, 'firstname')

    def findlastname(self, html):
        return self.getvalue('last_name', html, 'lastname')

    def findgender(self, html):
        return self.getvalue('gender', html, 'gender')

    def findbirthdate(self,html):
        return self.findbyre('"birthDate":"(.*?)"', html)

    def findbirthplace(self, html):
        section = self.findbyre('"birthPlace":\{(.*?)\}', html)
        if section:
            return self.findbyre('"name":"(.*?)"', section, 'city')

    def finddeathdate(self,html):
        return self.findbyre('"deathDate":"(.*?)"', html)

    def finddeathplace(self, html):
        section = self.findbyre('"deathPlace":\{(.*?)\}', html)
        if section:
            return self.findbyre('"name":"(.*?)"', section, 'city')

    def findnationalities(self, html):
        section = self.findbyre('(?s)<div class="artist-information-label">Nationality:</div>\s*<div class="artist-information-text">(.*?)</div>', html)
        if section:
            return self.findallbyre('([\w\s\-]+)', section, 'country')

    def findworkplaces(self, html):
        section = self.findbyre('(?s)<div class="artist-information-label">Places of Activity:</div>\s*<div class="artist-information-text">(.*?)</div>', html)
        if section:
            return self.findallbyre('>([^<>]*)</a>', section, 'city')

    def findmixedrefs(self, html):
        return [('P245', self.findbyre('/ulan/(\d+)', html))] + self.finddefaultmixedrefs(html, includesocial=False)
    


class WeberAnalyzer(UrlAnalyzer):
    def setup(self):
        self.dbid = None
        self.dbname = 'Weber Gesamtausgabe'
        self.hrtre = '<h2>Basisdaten</h2>(.*?)</ol>'
        self.language = 'de'

    def findinstanceof(self, html):
        return self.findbyre('"dc:subject" content="(.*?)"', html, 'instanceof')

    def findnames(self, html):
        return [self.findbyre('title" content="(.*?)(?: – |")', html)]

    def finddescriptions(self, html):
        return [
            self.findbyre('description" content="(.*?)"', html),
            self.findbyre('description" content="[^"]+?\.(.*?)"', html)
            ]

    def findbirthdate(self, html):
        return self.findbyre('(?s)<i class="fa fa-asterisk\s*"></i>\s*</div>\s*<div[^<>]*>\s*<span>(.*?)<', html)

    def findbirthplace(self, html):
        return self.findbyre('(?s)<i class="fa fa-asterisk\s*"></i>\s*</div>\s*<div[^<>]*>\s*<span>[^<>]*</span>\s*<span>\s*(?:in )([^<>]*)<', html, 'city')

    def findxsdeathdate(self, html):
        return self.findbyre('(?s)<strong>†</strong>\s*</div>\s*<div[^<>]*>\s*<span>(.*?)<', html)

    def finddeathplace(self, html):
        return self.findbyre('(?s)<strong>†</strong>\s*</div>\s*<div[^<>]*>\s*<span>[^<>]*</span>\s*<span>\s*(?:in )([^<>]*)<', html, 'city')

    def findoccupations(self, html):
        section = self.findbyre('(?s)<li class="media occupations">(.*?)</li>', html)
        if section:
            subsection = self.findbyre('(?s)<div class="media-body">(.*?)<', section)
            if subsection:
                return self.findallbyre('([^,]*)', subsection, 'occupation')

    def findresidences(self, html):
        section = self.findbyre('(?s)<li class="media residences">(.*?)</li>', html)
        if section:
            subsection = self.findbyre('(?s)<div class="media-body">(.*?)<', section)
            if subsection:
                return self.findallbyre('([^,]*)', subsection, 'city')


class BacklinkAnalyzer(Analyzer):    
    def setup(self):
        self.iswiki = True
        self.dbname = 'Wikidata Backlinks'
        self.dbproperty = None
        self.dbid = 'Q2013'
        self.urlbase = None
        self.sparqlquery = 'SELECT ?a ?b WHERE { ?a ?b wd:%s }'%self.id
        self.skipfirst = True
        self.hrtre = '()'
        self.language = 'en'

    def getrelations(self, relation, html):
        return [x.upper() for x in self.findallbyre('statement/([qQ]\d+)[^\{\}]+statement/%s'%relation, html)]

    def findspouses(self, html):
        return self.getrelations('P26', html)

    def findpartners(self, html):
        return self.getrelations('P451', html)

    def findpositions(self, html):
        return self.getrelations('P1308', html)

    def findpartofs(self, html):
        return self.getrelations('P527', html)

    def findparts(self, html):
        return self.getrelations('P361', html)

    def findstudents(self, html):
        return self.getrelations('P1066', html)

    def findteachers(self, html):
        return self.getrelations('P802', html)

    def finddocstudents(self, html):
        return self.getrelations('P184', html)

    def findadvisors(self, html):
        return self.getrelations('P185', html)

    def findchildren(self, html):
        return self.getrelations('P2[25]', html)

    def findsiblings(self, html):
        return self.getrelations('P3373', html)

    def findkins(self, html):
        return self.getrelations('P1038', html)

    def findnotableworks(self, html):
        return self.getrelations('P(?:50|57|86)', html)
    

if __name__ == '__main__':
    item = pywikibot.ItemPage(pywikibot.Site().data_repository(), sys.argv[1])
    bot = DataExtendBot()
    if len(sys.argv) > 2:
        bot.workon(item, sys.argv[2])
    else:
        bot.workon(item)
