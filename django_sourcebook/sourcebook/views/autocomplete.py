from dal import autocomplete
from django.db.models import Q
from sourcebook.models import Entity, Source

class SourceMatchesEntity(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Source.objects.none()
        if self.q:
            qs = Source.objects.filter(entity__id=self.q)
        return qs

class EntityAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Entity.objects.all()
        if self.q:
            qs = qs.filter(
                Q(name__iregex=f"(^|\s){self.q}") | Q(municipality__istartswith=self.q) | Q(locality__istartswith=self.q)
            )
        return qs

class SourceAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Source.objects.all()
        if self.q:
            qs = qs.filter(
                Q(last_name__istartswith=self.q) | Q(first_name__istartswith=self.q)
            )
        return qs