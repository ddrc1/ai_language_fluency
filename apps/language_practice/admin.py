from django.contrib import admin
from .models import Vocabulary, UserVocabulary


@admin.register(Vocabulary)
class VocabularyAdmin(admin.ModelAdmin):
    """Admin interface for Vocabulary model."""
    list_display = ('word_vocab', 'language', 'enable', 'created_at', 'updated_at')
    list_filter = ('language', 'enable')
    search_fields = ('word_vocab', 'language')
    readonly_fields = ('created_at', 'updated_at')
    # fieldsets = (
    #     ('Basic Information', {
    #         'fields': ('word_vocab', 'type', 'definition', 'example')
    #     }),
    #     ('Status', {
    #         'fields': ('enable',)
    #     }),
    #     ('Timestamps', {
    #         'fields': ('created_at', 'updated_at'),
    #         'classes': ('collapse',)
    #     }),
    # )


@admin.register(UserVocabulary)
class UserVocabularyAdmin(admin.ModelAdmin):
    """Admin interface for UserWordVocab model."""
    list_display = ('user__username', 'vocabulary__word_vocab', 'practice_count', 'last_practiced')
    search_fields = ('user__username', 'vocabulary__word_vocab')
    readonly_fields = ('created_at', 'updated_at')
    # fieldsets = (
    #     ('Relationship', {
    #         'fields': ('user', 'word_vocab')
    #     }),
    #     ('Progress', {
    #         'fields': ('level', 'times_practiced', 'last_practiced')
    #     }),
    #     ('Timestamps', {
    #         'fields': ('created_at', 'updated_at'),
    #         'classes': ('collapse',)
    #     }),
    # )
