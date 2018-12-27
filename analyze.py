import sys


def get_variants(flights):
    """Returns one cheapest, one fastest and one optimal variants.
    The 'optimal' flight is the cheapest flight among top 50 fastest ones."""
    try:
        fastest_list = get_fastest(flights)
        return {
            'cheapest': get_cheapest(flights)[0],
            'fastest': fastest_list[0],
            'optimal': get_cheapest(fastest_list[0:51])[0]
        }
    except Exception as e:
        print('Failed to get analytics: {}'.format(e), file=sys.stderr)
        return 'Sorry, the service is currently unavailable. :( Please try again later.'


def get_cheapest(flight_list):
    """Sorts the quotes by price, returns a list of sorted quotes."""
    cheapest = sorted(flight_list, key=lambda x: float(x['farebasis'][1]['adult']))
    return cheapest


def get_fastest(flight_list):
    """Sorts the quotes by duration, returns a list of sorted quotes."""
    fastest = sorted(flight_list, key=lambda x: x['duration_0']['total minutes'])
    query_type = flight_list[0]['flight_type']
    if query_type == 'one_way':
        return fastest
    else:
        return sorted(fastest, key=lambda x: x['duration_1']['total minutes'])
