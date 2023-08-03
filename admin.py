from django.contrib import admin
from .models import Corpus, Field

class CorpusAdmin(admin.ModelAdmin):
    readonly_fields = ['name']

    fieldsets = [
        (
            None,
            {
                'fields': [
                    'name',
                    'title',
                    'description',
                    'groups',
                    'description_page',
                    'image',
                ]
            }
        ), (
            'Content',
            {
                'fields': [
                    'category',
                    'languages',
                    'min_date',
                    'max_date',
                    'document_context',
                ]
            }
        ), (
            'Elasticsearch',
            {
                'fields': [
                    'es_index',
                    'es_alias',
                ]
            }
        ), (
            'Scans',
            {
                'fields': [
                    'scan_image_type',
                    'allow_image_download',
                ]
            }
        ), (
            'Word models',
            {
                'fields': ['word_models_present']
            }
        )
    ]

class FieldAdmin(admin.ModelAdmin):
    readonly_fields = ['corpus']

    fieldsets = [
        (
            None,
            {
                'fields': [
                    'name',
                    'corpus',
                    'display_name',
                    'description',
                    'hidden',
                    'downloadable',
                ]
            }
        ),
        (
            'Indexing options',
            {
                'fields': [
                    'es_mapping',
                    'indexed',
                    'required',
                ]
            }
        ), (
            'Search interface',
            {
                'fields': [
                    'search_filter',
                    'results_overview',
                    'searchable',
                    'search_field_core',
                    'sortable',
                    'primary_sort',
                ]
            }
        ), (
            'Visualisations',
            {
                'fields': [
                    'visualizations',
                    'visualization_sort',
                ]
            }
        )
    ]

admin.site.register(Corpus, CorpusAdmin)
admin.site.register(Field, FieldAdmin)
