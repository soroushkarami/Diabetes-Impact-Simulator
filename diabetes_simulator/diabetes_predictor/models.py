from django.db import models

class Patient(models.Model):
    pregnancies = models.IntegerField()
    glucose = models.IntegerField()
    bloodpressure = models.IntegerField()
    skinthickness = models.IntegerField()
    insulin = models.IntegerField()
    bmi = models.FloatField()
    pedigreefunc = models.FloatField()
    age = models.IntegerField()

    status = models.IntegerField()
    confidence = models.FloatField()

    q1 = models.IntegerField()
    q2 = models.IntegerField()
    q3 = models.IntegerField()
    q4 = models.IntegerField()
    q5 = models.IntegerField()
    q6 = models.IntegerField()
    q7 = models.IntegerField()
    q8 = models.IntegerField()
    q9 = models.IntegerField()
    score = models.IntegerField()

    def __str__(self):
        return f"ID: {self.id}, Age: {self.age}, {'Diabetic' if self.status == 1 else 'Healthy'}"