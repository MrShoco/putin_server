from mapdrive.models import Road, CellPopularity, City, Rating
from django.contrib.auth.models import User


def quantize_coord(val, quantization_factor=0.001):
    return int(val / quantization_factor) / int(1 / quantization_factor)


def inc_cell_score(lat, lon):
    cells = CellPopularity.objects.filter(lat=lat, lon=lon)
    if len(cells) == 0:
        cell_popularity = CellPopularity(lat=lat, lon=lon)
        cell_popularity.rating = 1.0
    else:
        assert len(cells) == 1
        cell_popularity = cells[0]
        cell_popularity.rating += 1.0
    cell_popularity.save()


def get_cell_score(lat, lon):
    cells = CellPopularity.objects.filter(lat=lat, lon=lon)
    if len(cells) == 0:
        cell_popularity = CellPopularity(lat=lat, lon=lon)
        cell_popularity.rating = 1.0
        cell_popularity.save()
    else:
        assert len(cells) == 1
        cell_popularity = cells[0]
    return cell_popularity.rating


def recalc_cells_popularity(road):
    x0, y0 = quantize_coord(road.x0), quantize_coord(road.y0)
    inc_cell_score(x0, y0)
    x1, y1 = quantize_coord(road.x1), quantize_coord(road.y1)
    inc_cell_score(x1, y1)


def get_city_by_road(road):
    x = (road.x0 + road.x1) / 2
    y = (road.y0 + road.y1) / 2
    
    min_dist = 1e6
    min_dist_city = None
    for city in City.objects.all():
        dist = (city.x - x) ** 2 + (city.y - y) ** 2
        if dist <= min_dist:
            min_dist_city = city
            min_dist = dist
    return min_dist_city


def recalc_users_ratings(road):
    for user in road.users.all():
        city = get_city_by_road(road)
        ratings = user.rating_set.filter(city_id=city.id)
        if len(ratings):
             rating = ratings[0]
        else:
             rating = Rating(rating=0.0)
             rating.city = city
             rating.user = user
             rating.save()
        x0, y0 = quantize_coord(road.x0), quantize_coord(road.y0)
        rating.rating += 1./get_cell_score(x0, y0)
        x1, y1 = quantize_coord(road.x1), quantize_coord(road.y1)
        rating.rating += 1./get_cell_score(x1, y1)
        rating.user = user
        rating.save()


def recalc_all_stats(road):
    recalc_cells_popularity(road)
    recalc_users_ratings(road)

