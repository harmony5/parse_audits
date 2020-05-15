from collections import Counter
import re

audit_regex = re.compile(r"((?<=====START====\n)(?P<content>.*?)(?=====END====))+")


def read_file(name, lines=True):
    with open(name, "r") as f:
        if lines:
            content = f.readlines()
        else:
            content = f.read()
    return content


def parse_audit(field, content):
    field_instances = []
    for i in range(len(content)):
        line = content[i]
        if line.find(field) != -1:
            old = content[i + 1]
            new = content[i + 2]

            # removes the start of the line indicating it's an old value, also removing whitespaces
            old = old[13:]
            new = new[13:]
            field_instances.append((i, (old, new)))

    return field_instances


def to_float(value):
    converted = value.replace(",", "").replace("\n", "")
    if converted == "":
        return 0.0

    converted = float(converted)
    return converted


def convert_num_values(values_tuple):
    a, b = values_tuple
    return (to_float(a), to_float(b))


# case-specific logic functions
def find_amount_field(field, content):
    return [(i, convert_num_values(d)) for i, d in parse_audit(field, content)]


def find_amount_diff(diff_list):
    return [(i, round(abs(a - b), 2)) for i, (a, b) in diff_list]


def filter_lines(predicate, list_to_filter):
    return [line for line, diff in filter(predicate, list_to_filter)]


def count_differences(diff_list):
    diffs = [b for a, b in diff_list]  # remove line numbers
    return Counter(diffs)


def diff_count_with_lines(diff_list):
    diff_count_list = count_differences(diff_list)
    diff_counts = set(diff_count_list.elements())
    with_line_numbers = [
        (
            [line for line, diff_1 in diff_list if diff_1 == diff_2],
            diff_2,
            diff_count_list[diff_2],
        )
        for diff_2 in diff_counts
    ]
    return with_line_numbers


audi = read_file("Auditoria Partida 03971.txt")
disponibles = find_amount_field("Disponible_Total", audi)
ejecutados = find_amount_field("Ejecutado_Total", audi)
reservas = find_amount_field("Reservas_Total", audi)

diff_disp = find_amount_diff(disponibles)
diff_ejec = find_amount_diff(ejecutados)
diff_resv = find_amount_diff(reservas)

equals_1_780_168_07 = lambda x: x[1] == 1_780_168.07

find_1_780_168_07_disp = filter_lines(equals_1_780_168_07, diff_disp)
find_1_780_168_07_ejec = filter_lines(equals_1_780_168_07, diff_ejec)
find_1_780_168_07_resv = filter_lines(equals_1_780_168_07, diff_resv)
