from django.core.management.base import BaseCommand, CommandError
from mapdrive.models import Track, File, Road
from datetime import datetime
from .parse_utils import process_json, process_gpx
from django.db.models import Q
from .users_ranking import recalc_all_stats


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('[{}] Start processing...'.format(datetime.now()))
        for track in Track.objects.filter(processed=False):
            for file in track.files.all():
                print('Processing "{}"'.format(file.file.name))
                extension = file.file.name.split('.')[-1]
                try:
                    if extension == 'json':
                        output = process_json(file.file)
                    elif extension == 'gpx':
                        output = process_gpx(file.file)
                    else:
                        print('Unknown format. Finish processing file')
                        continue
                except FileNotFoundError:
                    print('File not found. Finish processing file')
                    continue
                if output is not None:
                    print('File processed. Processing coordinates...')
                    coordinates = output['paths'][0]['points']['coordinates']
                    user = track.author
                    profile = user.profile
                    profile.total_distance += output['paths'][0]['distance']
                    profile.save()
                    for i in range(len(coordinates) - 1):
                        x0, y0 = coordinates[i]
                        x1, y1 = coordinates[i + 1]
                        roads = Road.objects.filter(Q(x0=x0, y0=y0, x1=x1, y1=y1) |
                                                    Q(x0=x1, y0=y1, x1=x0, y1=y0))
                        if len(roads):
                            road = roads[0]
                            road.last_user = user
                        else:
                            road = Road()
                            road.x0 = x0
                            road.y0 = y0
                            road.x1 = x1
                            road.y1 = y1
                            road.last_user = user
                            road.save()
                        road.users.add(user)
                        road.save()
                        recalc_all_stats(road)
                    print('Finish processing file')
                else:
                    print('Error in processing file "{}"'.format(file.file.name))
            track.processed = True
            track.save()

