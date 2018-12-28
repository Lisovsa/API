import sys


def get_variants(flight_list):
    """
    Analyzes flights and returns one cheapest, one fastest and one optimal variant in a dictionary.
    The 'optimal' flight is the cheapest flight among top 50 fastest ones.
    Arguments:
         - flight_list: the list of flights parsed from XML file.
    """
    try:
        fastest_list = get_fastest(flight_list)
        return {
            'cheapest': get_cheapest(flight_list)[0],
            'fastest': fastest_list[0],
            'optimal': get_cheapest(fastest_list[0:51])[0]
        }
    except Exception as e:
        print('Failed to get analytics: {}'.format(e), file=sys.stderr)
        return 'Sorry, the service is currently unavailable. :( Please try again later.'


def get_cheapest(flight_list):
    """
    Sorts the quotes by price, returns a list of sorted quotes.
    Arguments:
         - flight_list: the list of flights parsed from XML file.
    """
    cheapest = sorted(flight_list, key=lambda x: float(x['farebasis'][1]['adult']))
    return cheapest


def get_fastest(flight_list):
    """
    Sorts the quotes by duration, returns a list of sorted quotes.
    Arguments:
         - flight_list: the list of flights parsed from XML file.
    """
    fastest = sorted(flight_list, key=lambda x: x['duration_0']['total minutes'])
    query_type = flight_list[0].get('flight_type')
    if query_type == 'one_way':
        return fastest
    else:
        return sorted(fastest, key=lambda x: x['duration_1']['total minutes'])


def compare(one_way_list, return_list, one_way_file, return_file):
    """
    Compares results from 2 different XML files.
    Arguments:
         - one_way_list: the list of flights parsed from an XML file with one_way results,
         - return_list: the list of flights parsed from an XML file with return results,
         - one_way_file: filename of the file with one_way results,
         - return_file: filename of the file with return results.

    Returns a dictionary with the differences in results in two files.
    """
    result = {}
    one_way_elem = one_way_list[0]
    return_elem = return_list[0]

    for k, v in one_way_elem.items():
        for key, value in return_elem.items():

            # get difference in flight_type
            if k == key and k == 'flight_type':
                result[k] = {
                    one_way_file: v,
                    return_file: value
                }

            # get difference in fare_type
            if k == key and k == 'farebasis':
                for i in v:
                    for item in value:
                        one_way_fare = i.get('fare_type', None)
                        return_fare = item.get('fare_type', None)
                        if one_way_fare is not None and return_fare is not None:
                            result['fare_type'] = {
                                one_way_file: one_way_fare,
                                return_file: return_fare
                            }

            # get difference in dates
            if k == key and k == 'segments':
                one_way_time = v[0].get('departure_time', '2018-10-27T0000')[:10]
                r_first_dep_time = value[0].get('departure_time', '2018-10-22T0000')[:10]
                r_second_dep_time = value[-1].get('departure_time', '2018-10-30T0000')[:10]
                result['departure_datetime'] = {
                    one_way_file: {'DXB - BKK': one_way_time},
                    return_file: {'DXB - BKK': r_first_dep_time, 'BKK - DXB': r_second_dep_time}
                }

    return result
