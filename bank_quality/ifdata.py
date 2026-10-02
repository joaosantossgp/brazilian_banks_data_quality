"""Two-quarter IF.data collection, with explicit source failure states."""

import json
from pathlib import Path
from urllib.parse import urlencode, urljoin, urlsplit
from .archive import fetch, load_body
from .portal import export_portal

PERIODS = (201012, 202412)
APPROVED_PERIODS = (201012, 202312, 202412)
BASE = 'https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata'


def parse_odata(body: bytes) -> tuple[list[dict], str | None]:
    try:
        data = json.loads(body.decode('utf-8-sig'), parse_float=str)
    except (ValueError, UnicodeError) as error:
        raise ValueError('Not a valid UTF-8 OData JSON response') from error
    if not isinstance(data, dict) or not isinstance(data.get('value'), list):
        raise ValueError('OData response must contain a value array')
    if not all(isinstance(row, dict) for row in data['value']):
        raise ValueError('OData value array must contain objects')
    link = data.get('@odata.nextLink')
    if link is not None and not isinstance(link, str):
        raise ValueError('Invalid OData continuation link')
    return data['value'], link


def safe_next_link(link: str, base: str) -> str:
    target = urljoin(base, link)
    parts = urlsplit(target)
    if parts.scheme != 'https' or parts.netloc != 'olinda.bcb.gov.br' or not parts.path.startswith('/olinda/servico/IFDATA/versao/v1/odata/'):
        raise ValueError('Continuation leaves the official IF.data service')
    return target


def validate_values(rows: list[dict], period: int) -> None:
    for row in rows:
        required = {'AnoMes', 'TipoInstituicao', 'CodInst', 'Conta', 'NomeColuna', 'Saldo', 'NomeRelatorio'}
        if not required.issubset(row):
            raise ValueError('Missing IF.data value columns: ' + str(sorted(required - row.keys())))
        if str(row['AnoMes']) != str(period) or str(row['TipoInstituicao']) != '3' or row['NomeRelatorio'] != 'Resumo':
            raise ValueError('Response contains a period, institution type or report outside this pilot')
        if not isinstance(row['CodInst'], str) or not row['CodInst']:
            raise ValueError('Institution identifier must be a nonempty source string')


def _pages(url: str, raw: Path, label: str, context: dict, transport) -> dict:
    result = {'complete': False, 'rows': [], 'manifests': [], 'diagnostics': []}
    seen = set()
    for page in range(50):
        if url in seen:
            result['diagnostics'].append('Repeated continuation link')
            return result
        seen.add(url)
        accepted = None
        for attempt in range(2):
            item = transport(url, raw, f'{label}_page{page}_attempt{attempt+1}', context, timeout=30)
            result['manifests'].append(item)
            if item['outcome'] == 'ok' and item['http_status'] == 200:
                accepted = item
                break
        if accepted is None:
            result['diagnostics'].append('Request unavailable after two attempts; not historical absence')
            return result
        try:
            rows, link = parse_odata(load_body(accepted, raw))
            result['rows'].extend({**row, '_source_body': accepted['body_path'], '_source_sha256': accepted['sha256']} for row in rows)
            if link is None:
                result['complete'] = True
                return result
            url = safe_next_link(link, url)
        except ValueError as error:
            result['diagnostics'].append(str(error))
            return result
    result['diagnostics'].append('50-page safety cap reached; source incomplete')
    return result


def collect(root: Path, periods: tuple[int, ...] = PERIODS, transport=fetch,
            allow_fallback: bool = True, portal_transport=export_portal, portal_only: bool = False) -> dict:
    periods=tuple(periods)
    if not periods or len(set(periods))!=len(periods) or any(p not in APPROVED_PERIODS for p in periods):
        raise ValueError('Only explicit unique approved quarters 201012, 202312, 202412 are allowed')
    if periods not in (PERIODS,(202312,)):
        raise ValueError('New collections are limited to the original pilot or the single approved 202312 batch')
    if periods==(202312,) and not portal_only:
        raise ValueError('202312 requires explicit portal-only mode with aggregate execution/byte/reserve guards')
    if portal_only and not allow_fallback:raise ValueError('Portal-only conflicts with no-fallback')
    root = Path(root)
    raw = root / 'raw'
    if portal_only:
        result={'periods':list(periods),'institution_type':3,'report_name':'Resumo',
            'raw_directory':str(raw),'quarters':{},'discovery':{'complete':False,'diagnostics':[
            'Explicit official portal mode following documented earlier OData failures; no new-quarter OData availability claim']}}
        for period in periods:
            quarter={'values':[],'cadastro':[],'values_complete':False,'cadastro_complete':False,
                'sources':{},'diagnostics':[],'odata_attempt_state':'not_attempted_this_quarter'}
            result['quarters'][str(period)]=quarter
            try:quarter.update(portal_transport(period,raw))
            except (OSError,ValueError,RuntimeError) as error:
                quarter['diagnostics'].append(f'Official portal export failed: {type(error).__name__}: {error}')
        return result
    report = _pages(BASE + '/ListaDeRelatorio()?' + urlencode({'$format': 'json'}), raw, 'reports', {}, transport)
    codes = [str(row['NumeroRelatorio']) for row in report['rows'] if row.get('NomeRelatorio') == 'Resumo' and row.get('NumeroRelatorio')]
    result = {'periods': list(periods), 'institution_type': 3, 'report_name': 'Resumo',
              'discovery': report, 'quarters': {}, 'raw_directory': str(raw)}
    code = codes[0] if report['complete'] and len(set(codes)) == 1 else None
    for period in periods:
        quarter = {'values': [], 'cadastro': [], 'values_complete': False,
                   'cadastro_complete': False, 'source_mode': 'odata', 'diagnostics': [], 'sources': {}}
        result['quarters'][str(period)] = quarter
        if code is None:
            quarter['diagnostics'].append('Resumo report could not be verified from official report discovery')
        params = {'@AnoMes': period, '$format': 'json', '$top': 10000}
        cad_url = BASE + '/IfDataCadastro(AnoMes=@AnoMes)?' + urlencode(params)
        cad = _pages(cad_url, raw, f'cadastro_{period}', {'period': period, 'endpoint_parameters': {'AnoMes': period}}, transport)
        quarter['sources']['cadastro_odata'] = cad
        if cad['complete'] and all(str(row.get('Data')) == str(period) and isinstance(row.get('CodInst'), str) for row in cad['rows']):
            quarter['cadastro'] = cad['rows']
            quarter['cadastro_complete'] = True
        else:
            quarter['diagnostics'].append('Official OData cadastro unavailable or mismatched; entity-name coverage incomplete')
        params.update({'@TipoInstituicao': 3, '@Relatorio': "'" + (code or '') + "'"})
        val_url = BASE + '/IfDataValores(AnoMes=@AnoMes,TipoInstituicao=@TipoInstituicao,Relatorio=@Relatorio)?' + urlencode(params)
        values = _pages(val_url, raw, f'resumo_{period}', {'period': period, 'endpoint_parameters': {'AnoMes': period, 'TipoInstituicao': 3, 'Relatorio': code}}, transport) if code else {'complete':False,'rows':[],'manifests':[],'diagnostics':['Unverified report; request not sent']}
        quarter['sources']['values_odata'] = values
        if values['complete']:
            try:
                validate_values(values['rows'], period)
                quarter['values'] = values['rows']
                quarter['values_complete'] = True
            except ValueError as error:
                quarter['diagnostics'].append(str(error))
        if not quarter['values_complete'] and allow_fallback:
            quarter['diagnostics'].append('OData unavailable; attempting explicitly labeled official portal CSV fallback')
            try:
                fallback=portal_transport(period,raw)
                sources, diagnostics=quarter['sources'],quarter['diagnostics']
                quarter.update(fallback)
                quarter['sources']=sources
                quarter['diagnostics']=diagnostics+fallback.get('diagnostics',[])
            except (OSError,ValueError,RuntimeError) as error:
                quarter['diagnostics'].append(f'Official fallback failed: {type(error).__name__}: {error}')
    return result
