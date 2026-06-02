from rest_framework import serializers

class VocabularyResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    word_vocab = serializers.CharField()
    language = serializers.CharField()

class UserVocabularyResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user = serializers.CharField()
    word_vocab = serializers.CharField()
    practice_count = serializers.IntegerField()
    last_practiced = serializers.DateTimeField()