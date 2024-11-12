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
    """Load voter data records from a CSV file and create Voter model instances."""

    # Delete all existing Voter records
    Voter.objects.all().delete()
    
    # File path to the CSV
    file_path = os.path.join(settings.BASE_DIR, 'newton_voters.csv')
    
    # Open the file and discard the header
    with open(file_path, 'r') as f:
        headers = f.readline().strip()  # Read and ignore the header line

        # Go through the file line by line
        for line in f:
            fields = line.strip().split(',')
            
            try:
                # Create a new Voter instance using parsed fields
                voter = Voter(
                    last_name=fields[0],
                    first_name=fields[1],
                    street_number=fields[2],
                    street_name=fields[3],
                    apartment_number=fields[4] if fields[4] else None,
                    zip_code=fields[5],
                    date_of_birth=datetime.strptime(fields[6], '%Y-%m-%d'),
                    date_of_registration=datetime.strptime(fields[7], '%Y-%m-%d'),
                    party_affiliation=fields[8],
                    precinct_number=fields[9],
                    v20state=(fields[10].strip().lower() == 'true'),
                    v21town=(fields[11].strip().lower() == 'true'),
                    v21primary=(fields[12].strip().lower() == 'true'),
                    v22general=(fields[13].strip().lower() == 'true'),
                    v23town=(fields[14].strip().lower() == 'true'),
                    voter_score=int(fields[15])
                )
                # Print a confirmation message and save the instance
                print(f'Created voter: {voter}')
                voter.save()  # Save to the database

            except Exception as e:
                # Print an error message for any issues in parsing
                print(f"Exception occurred with fields: {fields}. Error: {e}")

    print("Done loading voter data.")
