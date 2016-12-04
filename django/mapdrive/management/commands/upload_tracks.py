from django.core.management.base import BaseCommand, CommandError
import os
from mapdrive.models import Track, File, User
from tqdm import tqdm

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'track_dir', type=str
        )

    def handle(self, *args, **options):
        user = User(id=1)
        track_dir = options['track_dir']
        for city_dir in os.listdir(track_dir):
            print(city_dir)
            for track_name in tqdm(os.listdir(os.path.join(track_dir, city_dir))):
                with open(os.path.join(track_dir, city_dir, track_name)) as f:
                    track_file = File()
                    track_file.file.save(track_name, f)
                    track_file.save()
                track = Track()
                track.author = user
                track.save()
                track.files.add(track_file)
                track.save()

