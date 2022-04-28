import datetime
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Subquery, OuterRef, F, Sum, Count
from collections import Counter
import more_itertools

from .models import Entry


def countriesWithMostNoOfTotalVaccines():
    entries = Entry.objects.all()
    result = []
    country = {}
    for entry in entries:
        if(entry.country not in country):
            country.update(
                {entry.country: 0 if entry.total_vaccinations is None else entry.total_vaccinations})
        else:
            if(country[entry.country] < 0 if entry.total_vaccinations is None else entry.total_vaccinations):
                country[entry.country] = entry.total_vaccinations

    sort_orders = dict(
        sorted(country.items(), key=lambda x: x[1], reverse=True))
    combinations = {}
    for k, v in more_itertools.take(5, sort_orders.items()):
        combinations.update({k: v})
    print(combinations)
    return combinations


def countriesWithLeastNoOfTotalVaccines():
    entries = Entry.objects.all()
    result = []
    country = {}
    for entry in entries:
        if(entry.country not in country):
            country.update(
                {entry.country: 0 if entry.total_vaccinations is None else entry.total_vaccinations})
        else:
            if(country[entry.country] < 0 if entry.total_vaccinations is None else entry.total_vaccinations):
                country[entry.country] = entry.total_vaccinations

    sort_orders = dict(
        sorted(country.items(), key=lambda x: x[1]))
    combinations = {}
    for k, v in more_itertools.take(5, sort_orders.items()):
        combinations.update({k: v})
    print(combinations)
    return combinations


def getLastestdata():
    entries = Entry.objects.all()
    result = []
    country = {}
    for entry in entries:
        if(entry.country not in country):
            country.update({entry.country: list([entry.date, entry.country])})
        else:
            if(country[entry.country][0] < entry.date):
                country[entry.country] = list([entry.date, entry.country])
    return list(country)


def countries():
    entries = Entry.objects.all()
    countries = []
    for entry in entries:
        if (entry.country not in countries):
            countries.append(entry.country)

    return len(countries)


def unique_Vaccine():
    entries = Entry.objects.all()
    uniqueVaccine = []
    for entry in entries:
        vaccines = list(entry.vaccines.split(", "))
        for vaccine in vaccines:
            if (vaccine not in uniqueVaccine):
                uniqueVaccine.append(vaccine)
    return uniqueVaccine


def max_Vaccine_Shots_By_Country_In_One_Day():
    entries = Entry.objects.all()
    result = ['0', 'country', 'date']
    for entry in entries:
        if(entry.daily_vaccinations is not None and entry.daily_vaccinations > int(result[0])):
            result[0] = entry.daily_vaccinations
            result[1] = entry.country
            result[2] = str(entry.date)
    return result


def home(request):
    total_vaccines = Entry.objects.all().aggregate(Sum("daily_vaccinations"))[
        "daily_vaccinations__sum"
    ]

    args = {}
    text = "hello world"
    args['mytext'] = text
    args['uniqueVaccine'] = unique_Vaccine()
    args['total_vaccines'] = total_vaccines
    args['max_Vaccine_Shots_By_Country_In_One_Day'] = max_Vaccine_Shots_By_Country_In_One_Day()
    args['countries'] = countries()
    args['country'] = getLastestdata()
    args['countriesWithLeastNoOfTotalVaccines'] = countriesWithLeastNoOfTotalVaccines()
    args['countriesWithMostNoOfTotalVaccines'] = countriesWithMostNoOfTotalVaccines()
    return render(request, template_name="home.html", context=args)


def mostVacicinatedCountry(request):
    qs = Entry.objects.all()
    d = {}
    for i in qs:
        if(i.country not in d):
            d.update(
                {i.country: [0 if i.people_vaccinated_per_hundred is None else i.people_vaccinated_per_hundred, i.date]})
        else:
            if(d[i.country][1] < i.date):
                d[i.country] = [
                    0 if i.people_vaccinated_per_hundred is None else i.people_vaccinated_per_hundred, i.date]
    sort_orders = dict(sorted(d.items(), key=lambda x: x[1], reverse=True))
    combinations = {}
    for k, v in more_itertools.take(10, sort_orders.items()):
        combinations.update({k: v[0]})
    return JsonResponse(data={"combinations": combinations})


def linechart(request):
    countries = [
        "United Kingdom",
        "Germany",
        "France",
        "Israel",
        "United States",
        "India",
        "Brazil",
        "Turkey",
        "Chile",
        "Russia",
    ]
    cutoff_date = datetime.datetime.today() - datetime.timedelta(days=500)
    datasets = []
    for country in countries:
        qs = Entry.objects.filter(country=country, date__gte=cutoff_date)
        data = [
            {"x": entry.date, "y": entry.total_vaccinations} for entry in qs
        ]
        datasets.append({"label": country, "data": data})
    return JsonResponse(data={"datasets": datasets})


def piechart(request):
    total_vaccines = Entry.objects.all().aggregate(Sum("daily_vaccinations"))[
        "daily_vaccinations__sum"
    ]
    qs = (
        Entry.objects.values("country")
        .annotate(total=Sum("daily_vaccinations"))
        .order_by("-total")[:9]
    )
    # calculate percentage and rest
    combinations = {
        entry["country"]: (entry["total"] / total_vaccines) for entry in qs
    }
    combinations["other"] = 1 - sum(entry["total"]
                                    for entry in qs) / total_vaccines
    return JsonResponse(data={"combinations": combinations})


def table(request):

    return JsonResponse(data={"a": 1})
