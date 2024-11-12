from django.db import models
import csv
from datetime import datetime
from django.conf import settings
import os


class Voter(models.Model):
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    street_number = models.CharField(max_length=10)
    street_name = models.CharField(max_length=100)
    apartment_number = models.CharField(max_length=10, blank=True, null=True)
    zip_code = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    date_of_registration = models.DateField()
    party_affiliation = models.CharField(max_length=50)
    precinct_number = models.CharField(max_length=10)
    v20state = models.BooleanField()
    v21town = models.BooleanField()
    v21primary = models.BooleanField()
    v22general = models.BooleanField()
    v23town = models.BooleanField()
    voter_score = models.IntegerField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.precinct_number}"

def load_data():
    file_path = os.path.join(settings.BASE_DIR, 'newton_voters.csv')
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            Voter.objects.create(
                last_name=row['Last Name'],
                first_name=row['First Name'],
                street_number=row['Residential Address - Street Number'],
                street_name=row['Residential Address - Street Name'],
                apartment_number=row.get('Residential Address - Apartment Number', None),
                zip_code=row['Residential Address - Zip Code'],
                date_of_birth=datetime.strptime(row['Date of Birth'], '%Y-%m-%d'),
                date_of_registration=datetime.strptime(row['Date of Registration'], '%Y-%m-%d'),
                party_affiliation=row['Party Affiliation'],
                precinct_number=row['Precinct Number'],
                v20state=row['v20state'] == 'True',
                v21town=row['v21town'] == 'True',
                v21primary=row['v21primary'] == 'True',
                v22general=row['v22general'] == 'True',
                v23town=row['v23town'] == 'True',
                voter_score=int(row['voter_score']),
            )

