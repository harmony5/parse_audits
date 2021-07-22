#%%
from pprint import pprint
from parse_audits.parsers import parse_audit_entries_from_text, parse_audit_text_as_json
from parse_audits.utils import _read_file

test = _read_file(r'C:\Users\pc\Documents\Projects\parse_audits\sample_audit.txt')

audits = [*parse_audit_entries_from_text(test)]

pprint(audits)