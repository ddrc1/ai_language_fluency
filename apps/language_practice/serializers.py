from rest_framework import serializers

from apps.language_practice.models import Language, Vocabulary, UserVocabulary


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'

    def validate(self, data: dict):
        name = data.get('name')

        if name and Language.objects.filter(name__iexact=name).exists():
            raise serializers.ValidationError("This language already exists.")

        return data

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "name": instance.name,
            "enable": instance.enable,
        }


class VocabularySerializer(serializers.ModelSerializer):
    language = serializers.PrimaryKeyRelatedField(queryset=Language.objects.filter(enable=True))

    class Meta:
        model = Vocabulary
        fields = ['id', 'word_vocab', 'language', 'enable', 'created_at', 'updated_at']

    def validate(self, data: dict):
        word_vocab = data.get('word_vocab')
        language = data.get('language')

        if word_vocab and language and Vocabulary.objects.filter(word_vocab__iexact=word_vocab, language=language).exists():
            raise serializers.ValidationError("This word already exists.")

        return data

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "word_vocab": instance.word_vocab,
            "language": instance.language.name,
            "enable": instance.enable,
        }


class UserVocabularySerializer(serializers.ModelSerializer):
    vocabulary = serializers.PrimaryKeyRelatedField(queryset=Vocabulary.objects.filter(enable=True))
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = UserVocabulary
        fields = ['id', 'user', 'vocabulary', 'practice_count', 'last_practiced', 'enable', 'created_at', 'updated_at']

    def validate(self, data: dict):
        request = self.context.get('request')
        user = request.user if request else None
        vocabulary = data.get('vocabulary')

        if user and vocabulary and UserVocabulary.objects.filter(user=user, vocabulary=vocabulary, enable=True).exists():
            raise serializers.ValidationError("This user is already practicing this word.")
        
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user

        try:
            instance: UserVocabulary = UserVocabulary.objects.get(user=validated_data['user'], vocabulary=validated_data['vocabulary'])
            instance.enable = True
            instance.save()

            return instance
        except UserVocabulary.DoesNotExist:
            return super().create(validated_data)
        

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "user": instance.user.username,
            "word_vocab": instance.vocabulary.word_vocab,
            "language": instance.vocabulary.language.name,
            "practice_count": instance.practice_count,
            "last_practiced": instance.last_practiced,
            "ready_for_practice": instance.ready_for_practice,
        }