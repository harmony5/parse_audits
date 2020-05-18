from collections import Counter
import regex as reg
import re
from more_itertools import take, nth


def read_file(name, lines=True):
    with open(name, "r") as f:
        if lines:
            content = f.readlines()
        else:
            content = f.read()
    return content


# def parse_audit(field, content):
#     field_instances = []
#     for i in range(len(content)):
#         line = content[i]
#         if line.find(field) != -1:
#             old = content[i + 1]
#             new = content[i + 2]

#             # removes the start of the line indicating it's an old value, also removing whitespaces
#             old = old[13:]
#             new = new[13:]
#             field_instances.append((i, (old, new)))

#     return field_instances


# def to_float(value):
#     converted = value.replace(",", "").replace("\n", "")
#     if converted == "":
#         return 0.0

#     converted = float(converted)
#     return converted


# def convert_num_values(values_tuple):
#     a, b = values_tuple
#     return (to_float(a), to_float(b))


# # case-specific-logic functions
# def find_amount_field(field, content):
#     return [(i, convert_num_values(d)) for i, d in parse_audit(field, content)]


# def find_amount_diff(diff_list):
#     return [(i, round(abs(a - b), 2)) for i, (a, b) in diff_list]


# def filter_lines(predicate, list_to_filter):
#     return [line for line, diff in filter(predicate, list_to_filter)]


# def count_differences(diff_list):
#     diffs = [b for a, b in diff_list]  # remove line numbers
#     return Counter(diffs)


# def diff_count_with_lines(diff_list):
# diff_count_list = count_differences(diff_list)
# diff_counts = set(diff_count_list.elements())
# with_line_numbers = [
#     (
#         [line for line, diff_1 in diff_list if diff_1 == diff_2],
#         diff_2,
#         diff_count_list[diff_2],
#     )
#     for diff_2 in diff_counts
# ]
# return with_line_numbers


# audi = read_file(r"C:\Users\pc\Downloads\Trabajo\Codigo CQ\Auditoria Partida 03971.txt")
# disponibles = find_amount_field("Disponible_Total", audi)
# ejecutados = find_amount_field("Ejecutado_Total", audi)
# reservas = find_amount_field("Reservas_Total", audi)

# diff_disp = find_amount_diff(disponibles)
# diff_ejec = find_amount_diff(ejecutados)
# diff_resv = find_amount_diff(reservas)

# equals_1_780_168_07 = lambda x: x[1] == 1_780_168.07

# find_1_780_168_07_disp = filter_lines(equals_1_780_168_07, diff_disp)
# find_1_780_168_07_ejec = filter_lines(equals_1_780_168_07, diff_ejec)
# find_1_780_168_07_resv = filter_lines(equals_1_780_168_07, diff_resv)


# Regex v1: ((?<=====START====\n)(?P<content>.*?)(?=====END====))+
# Regex v2 (v1.5 had . for the entire fields group)
# ((?<=====START====\n)                               # Start of audit entry
#         (?P<entry>                                          # ^^^^^

#         Time\s+:\s+                                         # Time of the modification
#         (?P<time>
#             (?P<year>\d{4})-
#             (?P<month>\d{2})-
#             (?P<day>\d{2})\s+
#             (?P<hour>\d{2}):
#             (?P<minute>\d{2}):
#             (?P<second>\d{2})\s+
#             (?P<timezone>[+-]?\d{2}:\d{2}))(?:\n|\r\n?)

#         Schema\s+Rev\s+:\s+                                 # Schema revision
#         (?P<schema>\d+)(?:\n|\r\n?)

#         User\s+Name\s+:\s+                                  # User that modified the record
#         (?P<user_name>[A-Za-z ]+)(?:\n|\r\n?)

#         User\s+Login\s+:\s+                                 # Login used
#         (?P<user_login>[uU]\d+)(?:\n|\r\n?)

#         User\s+Groups\s+:\s+                                # Groups, duh!
#         (?P<user_groups>[\w\b ]+)(?:\n|\r\n?)

#         Action\s+:\s+                                       # Action executed on the record
#         (?P<action>[\w\b ]+)(?:\n|\r\n?)

#         State\s+:\s+                                        # State of the record
#         (?P<state>[\w\b ]+)(?:\n|\r\n?)

#         ==Fields==(?:\n|\r\n?)
#         (?P<fields>
#             ((?P<fieldname>\w+(?=\s+\(\d+:\d+\)))(?:\n|\r\n?)  # The fieldname, followed by delta (old value's length compared to the new value's), newline
#                 \s+Old\s+:\s+                               # Field's old value
#                 (?P<old_value>.+?(?=\s+New))(?:\n|\r\n?)    # Any character until the new value
#                 \s+New\s+:\s+
#                 (?P<new_value>.+?(?=\w+\s+\(\d+:\d+\)       # Any character until another fieldname or the END of the audit entry
#                                     |====END====))
#             )+)(?:\n|\r\n?))
#         (?=====END====))+

# \s+ used to indicate spaces and tabs. (?:\n|\r\n?) for newlines, (\n, \r, \r\n) may be found
pat0 = r"""(?<=====START====\n)                               # Start of audit entry
        (?P<entry>                                          
        
        (?<=Time\s{11}:\s{4})                                    # Time of the modification
        (?P<time>
                \d{4}-                                      # Year
                \d{2}-                                      # Month
                \d{2}\s                                    # Day
                \d{2}:                                      # Hour
                \d{2}:                                      # Minute
                \d{2}\s                                    # Second
                [+-]?\d{2}:\d{2}                            # Timezone
        )(?=\n)
        
        (?<=Schema\sRev\s{5}:\s{4})                            # Schema revision
        (?P<schema>\d+)(?:\n|\r\n?)
        
        (?:User\s+Name\s+:\s+)                             # User that modified the record
        (?P<user_name>[A-Za-z ]+)(?:\n|\r\n?)
        
        (?:User\s+Login\s+:\s+)                            # Login used
        (?P<user_login>[uU]\d+)(?:\n|\r\n?)
        
        (?:User\s+Groups\s+:\s+)                           # Groups, duh!
        (?P<user_groups>[\w\b ]+)(?:\n|\r\n?)
        
        (?:Action\s+:\s+)                                  # Action executed on the record
        (?P<action>[\w\b ]+)(?:\n|\r\n?)
        
        (?:State\s+:\s+)                                   # State of the record
        (?P<state>[\w\b ]+)(?:\n|\r\n?)
        
        (?:==Fields==(\n|\r\n?))
        (?P<fields>
            (?P<fieldname>\w+(?:\s+\(\d+:\d+\)))            # Fieldname followed by (old_length:new_length)
            
            (?:(\n|\r\n?)\s+Old\s+:\s+)
            (?P<old>.+?(?:(\n|\r\n?)\s+New\s+:))

            (?:(\n|\r\n?)\s+New\s+:\s+)
            (?P<new>.+?(?:((\n|\r\n?)\w+\s+\(\d+:\d+\)(\n|\r\n?))|((\n|\r\n?)====END====)))     # All characters followed by another field or the end of the entry (====END====)
        )+
        
        )(?:====END====)"""  # End of audit entry


pat = (
    r"(?<=====START====\n)"
    r"(?P<entry>"
    r"(?<=Time           :    )"
    r"(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]?\d{2}:\d{2})(?=\n)"  # YY-MM-DD HH:mm:SS Timezone
    r"(?<=Schema Rev     :    )"
    r"(?P<schema>\d+?)(?=\n)"
    r"(?<=User Name      :    )"
    r"(?P<user_name>[A-Za-z ]+?)(?=\n)"
    r"(?<=User Login     :    )"
    r"(?P<user_login>[uU]\d+?)(?=\n)"
    r"(?<=User Groups    :    )"
    r"(?P<user_groups>[\w\b ]+?)(?=\n)"
    r"(?<=Action         :    )"
    r"(?P<action>[\w\b ]+?)(?=\n)"
    r"(?<=State          :    )"
    r"(?P<state>[\w\b ]+?)(?=\n)"
    r"(?<===Fields==\n)"
    r"(?P<field>.+?"
    # r"(?P<fieldname>\w+?)(?:\s+)(?P<delta>\(\d+:\d+\))(?=\n)"
    # r"(?<=    Old :    )"
    # r"(?P<old>.+?)(?=\n    New :    )"
    # r"(?<=    New :    )"
    # r"(?P<new>.+?)(?=(\n\w+\s+\(\d+:\d+\)\n)|\n====END====)"  # Til' finding a new field or the END of the entry
    r")"  # +"  # There can be multiple fields
    r")(?=====END====)"
)

are1 = reg.compile(pat, reg.DOTALL)

are0 = re.compile(pat, re.DOTALL)

par = read_file(
    r"C:\Users\pc\Downloads\Trabajo\Codigo CQ\Auditoria Partida 03971.txt", False
)

m = reg.match(are1, par)
m0 = re.match(are0, par)

print(f"Regex:\n{m is None=}")
print(f"\nRe:\n{m0 is None=}")
r"""((?<=====START====\n)                               # Start of audit entry
        (?P<entry>                                          # ^^^^^
        
        (?<=Time\s+:\s+)                                    # Time of the modification
        (?P<time>
                \d{4}-                                      # Year
                \d{2}-                                      # Month
                \d{2}\s+                                    # Day
                \d{2}:                                      # Hour
                \d{2}:                                      # Minute
                \d{2}\s+                                    # Second
                [+-]?\d{2}:\d{2}                            # Timezone
        )(?=\n|\r\n?)
        
        (?<=Schema\s+Rev\s+:\s+)                            # Schema revision
        (?P<schema>\d+)(?=\n|\r\n?)
        
        (?<=User\s+Name\s+:\s+)                             # User that modified the record
        (?P<user_name>[A-Za-z ]+)(?=\n|\r\n?)
        
        (?<=User\s+Login\s+:\s+)                            # Login used
        (?P<user_login>[uU]\d+)(?=\n|\r\n?)
        
        (?<=User\s+Groups\s+:\s+)                           # Groups, duh!
        (?P<user_groups>[\w\b ]+)(?=\n|\r\n?)
        
        (?<=Action\s+:\s+)                                  # Action executed on the record
        (?P<action>[\w\b ]+)(?=\n|\r\n?)
        
        (?<=State\s+:\s+)                                   # State of the record
        (?P<state>[\w\b ]+)(?=\n|\r\n?)
        
        (?<===Fields==(\n|\r\n?))
        (?P<fields>
            (?P<fieldname>\w+(?=\s+\(\d+:\d+\)))            # Fieldname followed by (old_length:new_length)
            
            (?<=(\n|\r\n?)\s+Old\s+:\s+)
            (?P<old>.+?(?=(\n|\r\n?)\s+New\s+:))

            (?<=(\n|\r\n?)\s+New\s+:\s+)
            (?P<new>.+?(?=((\n|\r\n?)\w+\s+\(\d+:\d+\)(\n|\r\n?))|((\n|\r\n?)====END====)))     # All characters followed by another field or the end of the entry (====END====)
        )+
        
        )(?=====END====))+"""
