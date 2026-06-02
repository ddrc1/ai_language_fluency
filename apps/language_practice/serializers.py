from rest_framework import serializers

from apps.language_practice.models import Vocabulary, UserVocabulary

class VocabularySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vocabulary
        fields = '__all__'

    def validate(self, data: dict):
        word_vocab = data.get('word_vocab')
        language = data.get('language')

        if Vocabulary.objects.filter(word_vocab=word_vocab.lower(), language=language.lower()).exists():
            raise serializers.ValidationError("This word already exists.")

        return data

    def to_representation(self, instance):
        representation = {
            "id": instance.id,
            "word_vocab": instance.word_vocab,
            "language": instance.language
        }

        return representation
    

class UserVocabularySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserVocabulary
        fields = '__all__'

    def validate(self, data: dict):
        user = data.get('user')
        vocabulary = data.get('vocabulary')

        if UserVocabulary.objects.filter(user=user, vocabulary=vocabulary).exists():
            raise serializers.ValidationError("This user is already practicing this word.")

        return data

    def create(self, validated_data):
        Vocabulary.objects.get_or_create(**validated_data['vocabulary'])
        user_vocab = UserVocabulary.objects.create(
            user=validated_data['user'],
            vocabulary=validated_data['vocabulary']
        )

        return user_vocab
    
    def to_representation(self, instance):
        representation = {
            "id": instance.id,
            "user": instance.user.username,
            "word_vocab": instance.vocabulary.word_vocab,
            "practice_count": instance.practice_count,
            "last_practiced": instance.last_practiced
        }

        return representation