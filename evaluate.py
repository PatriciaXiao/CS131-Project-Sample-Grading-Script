import re
import json

EPS = 1e-5

def parse_float(full_string):
    return re.findall(r"[-+]?\d*\.\d+|\d+", full_string)

def evaluate_json(json_data, len_results=0):
    if isinstance(json_data, list):
        # contains only the place info
        json_data = {"results": json_data}
    format_correct = len(set(["html_attributions", "results", "status"]) - set(json_data.keys())) == 0
    # otherwise there's a missing field
    result_valid = json_data.get("status") == "OK"
    result_length_correct = len(json_data.get("results", [])) <= len_results
    return format_correct, result_valid, result_length_correct

def evaluate_info(feedback_string, expected_server, expected_client, expected_lat, expected_lng):
    feedback_elem = [e for e in feedback_string.split() if len(e) > 0]
    correct_length = len(feedback_elem) == 6
    location = correct_length and parse_float(feedback_elem[4])
    timediff = correct_length and parse_float(feedback_elem[2])
    timestmp = correct_length and parse_float(feedback_elem[5])
    correct_format = correct_length \
                    and feedback_elem[0] == "AT" \
                    and len(timediff) == 1 \
                    and len(timestmp) == 1 \
                    and len(location) == 2
    correct_content = correct_length \
                    and feedback_elem[1] == expected_server \
                    and feedback_elem[3] == expected_client \
                    and len(location) == 2 \
                    and abs(float(location[0]) - float(expected_lat)) <= EPS \
                    and abs(float(location[1]) - float(expected_lng)) <= EPS
    return correct_length, correct_format, correct_content

def compare_info(string1, string2):
    elem_lst1 = [e for e in string1.split() if len(e) > 0]
    elem_lst2 = [e for e in string2.split() if len(e) > 0]
    same_length = len(elem_lst1) == len(elem_lst2)
    same_content = True
    for i in range(min(len(elem_lst1), len(elem_lst2))):
        if string1[i] != string2[i]:
            same_content = False
            break
    return same_length, same_content

def count_score(lst, w):
    cnt = 0
    total = 0
    for elem, weight in zip(lst, w):
        if isinstance(elem, bool):
            cnt += weight if elem else 0
            total += weight
        else:
            for e in elem:
                cnt += weight if e else 0
                total += weight
    return cnt, total

def evaluate_flooding(results, target_results, max_item):
    first_line, json_data = target_results
    json_correctness = evaluate_json(json_data, max_item)
    same_first_line = True
    same_json = True
    robustness = True
    for res in results:
        first_line_tmp, json_data_tmp = res
        if robustness:
            robustness = first_line_tmp != "CRUSH"
        if same_first_line:
            first_line_judge = compare_info(first_line_tmp, first_line)
            same_first_line = first_line_judge[0] and first_line_judge[1]
        if same_json:
            same_json = evaluate_json(json_data_tmp, max_item) == json_correctness
    return same_first_line, same_json, robustness

def compare_lists(list1, list2):
    match = list()
    for elem in list1:
        if elem not in list2:
            match.append(False)
        else:
            match.append(True)
            list2.pop(list2.index(elem))
    return tuple(match)

