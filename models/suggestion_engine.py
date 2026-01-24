"""
SuggestionEngine: Maps detected features (emotion, age, gender) to recommended filters/templates
"""

from typing import Dict, List, Optional
from .model_manager import get_model_manager


class SuggestionEngine:
    """Engine for suggesting filters/templates based on user characteristics"""

    # Emotion to filter mappings
    EMOTION_FILTER_MAP = {
        'happy': ['none', 'pastel_glow', 'sakura', 'sparkle', 'polaroid', 'heart_bokeh'],
        'sad': ['sepia', 'vintage', 'warm_tone', 'soft_skin'],
        'surprise': ['rainbow_leak', 'comic_pastel', 'cartoon'],
        'angry': ['cool_tone', 'grayscale', 'edge_detection'],
        'fear': ['blur', 'soft_skin', 'pastel_glow'],
        'disgust': ['cartoon', 'comic_pastel', 'pencil_sketch'],
        'neutral': ['portrait_pro', 'smart_beauty', 'none']
    }

    # Emotion to template mappings
    EMOTION_TEMPLATE_MAP = {
        'happy': ['1x4', 'pastel_pink', 'grid_modern'],
        'sad': ['classic_strip', 'pastel_pink'],
        'surprise': ['2x2', 'grid_modern'],
        'angry': ['1x4', 'classic_strip'],
        'fear': ['2x2', 'pastel_pink'],
        'disgust': ['1x4', 'grid_modern'],
        'neutral': ['2x2', 'classic_strip', 'grid_modern']
    }

    # Age range to filter mappings
    AGE_FILTER_MAP = {
        '13-19': ['sparkle', 'rainbow_leak', 'comic_pastel', 'cartoon', 'heart_bokeh'],
        '20-34': ['pastel_glow', 'sakura', 'polaroid', 'portrait_pro', 'smart_beauty'],
        '35-54': ['sepia', 'vintage', 'soft_skin', 'warm_tone'],
        '55+': ['sepia', 'vintage', 'grayscale', 'warm_tone']
    }

    # Gender to filter mappings
    GENDER_FILTER_MAP = {
        'male': ['cool_tone', 'grayscale', 'edge_detection', 'portrait_pro'],
        'female': ['pastel_glow', 'sakura', 'soft_skin', 'smart_beauty', 'sparkle'],
        'other': ['none', 'polaroid', 'comic_pastel']
    }

    @staticmethod
    def suggest_filters(emotion: Optional[str] = None,
                       age_range: Optional[str] = None,
                       gender: Optional[str] = None,
                       top_k: int = 3) -> List[Dict[str, any]]:
        """
        Suggest filters based on user characteristics.

        Args:
            emotion: detected emotion
            age_range: age range string
            gender: gender string
            top_k: number of suggestions to return

        Returns:
            List of suggested filters with scores
        """
        filter_scores = {}

        # Emotion-based suggestions
        if emotion and emotion in SuggestionEngine.EMOTION_FILTER_MAP:
            emotion_filters = SuggestionEngine.EMOTION_FILTER_MAP[emotion]
            for f in emotion_filters:
                filter_scores[f] = filter_scores.get(f, 0) + 3  # High weight for emotion

        # Age-based suggestions
        if age_range and age_range in SuggestionEngine.AGE_FILTER_MAP:
            age_filters = SuggestionEngine.AGE_FILTER_MAP[age_range]
            for f in age_filters:
                filter_scores[f] = filter_scores.get(f, 0) + 2

        # Gender-based suggestions
        if gender and gender in SuggestionEngine.GENDER_FILTER_MAP:
            gender_filters = SuggestionEngine.GENDER_FILTER_MAP[gender]
            for f in gender_filters:
                filter_scores[f] = filter_scores.get(f, 0) + 1

        # If no characteristics provided, return popular defaults
        if not filter_scores:
            default_filters = ['none', 'polaroid', 'soft_skin', 'pastel_glow']
            for f in default_filters:
                filter_scores[f] = 1

        # Sort by score and return top_k
        sorted_filters = sorted(filter_scores.items(), key=lambda x: x[1], reverse=True)
        result = []

        for filter_name, score in sorted_filters[:top_k]:
            result.append({
                'filter_name': filter_name,
                'score': score,
                'reason': SuggestionEngine._get_suggestion_reason(
                    filter_name, emotion, age_range, gender
                )
            })

        return result

    @staticmethod
    def suggest_templates(emotion: Optional[str] = None,
                         age_range: Optional[str] = None,
                         gender: Optional[str] = None,
                         top_k: int = 2) -> List[Dict[str, any]]:
        """
        Suggest templates based on user characteristics.

        Args:
            emotion: detected emotion
            age_range: age range string
            gender: gender string
            top_k: number of suggestions to return

        Returns:
            List of suggested templates with scores
        """
        template_scores = {}

        # Emotion-based suggestions
        if emotion and emotion in SuggestionEngine.EMOTION_TEMPLATE_MAP:
            emotion_templates = SuggestionEngine.EMOTION_TEMPLATE_MAP[emotion]
            for t in emotion_templates:
                template_scores[t] = template_scores.get(t, 0) + 2

        # Age-based template preferences (younger prefer colorful, older prefer classic)
        if age_range:
            if age_range in ['13-19', '20-34']:
                youthful_templates = ['2x2', 'grid_modern', 'pastel_pink']
                for t in youthful_templates:
                    template_scores[t] = template_scores.get(t, 0) + 1
            else:  # Older users
                classic_templates = ['1x4', 'classic_strip']
                for t in classic_templates:
                    template_scores[t] = template_scores.get(t, 0) + 1

        # If no characteristics provided, return popular defaults
        if not template_scores:
            default_templates = ['2x2', '1x4', 'classic_strip']
            for t in default_templates:
                template_scores[t] = 1

        # Sort by score and return top_k
        sorted_templates = sorted(template_scores.items(), key=lambda x: x[1], reverse=True)
        result = []

        for template_name, score in sorted_templates[:top_k]:
            result.append({
                'template_name': template_name,
                'score': score,
                'reason': SuggestionEngine._get_template_reason(
                    template_name, emotion, age_range, gender
                )
            })

        return result

    @staticmethod
    def _get_suggestion_reason(filter_name: str, emotion: Optional[str],
                              age_range: Optional[str], gender: Optional[str]) -> str:
        """Generate human-readable reason for filter suggestion"""
        reasons = []

        if emotion and filter_name in SuggestionEngine.EMOTION_FILTER_MAP.get(emotion, []):
            reasons.append(f"suits {emotion} mood")

        if age_range and filter_name in SuggestionEngine.AGE_FILTER_MAP.get(age_range, []):
            reasons.append(f"popular with {age_range} age group")

        if gender and filter_name in SuggestionEngine.GENDER_FILTER_MAP.get(gender, []):
            reasons.append(f"commonly chosen by {gender} users")

        if not reasons:
            reasons.append("popular choice")

        return ", ".join(reasons)

    @staticmethod
    def _get_template_reason(template_name: str, emotion: Optional[str],
                            age_range: Optional[str], gender: Optional[str]) -> str:
        """Generate human-readable reason for template suggestion"""
        reasons = []

        if emotion and template_name in SuggestionEngine.EMOTION_TEMPLATE_MAP.get(emotion, []):
            reasons.append(f"matches {emotion} expression")

        if age_range:
            if age_range in ['13-19', '20-34'] and template_name in ['2x2', 'grid_modern']:
                reasons.append("modern and vibrant")
            elif age_range in ['35-54', '55+'] and template_name in ['1x4', 'classic_strip']:
                reasons.append("classic and timeless")

        if not reasons:
            reasons.append("versatile option")

        return ", ".join(reasons)

    @staticmethod
    def get_personalized_suggestions(image) -> Dict[str, any]:
        """
        Analyze image and return comprehensive personalized suggestions.

        Args:
            image: PIL Image to analyze

        Returns:
            Dict with emotion, suggested_filters, suggested_templates
        """
        model_manager = get_model_manager()

        try:
            # Detect face and emotion
            faces = model_manager.detect_faces(image)
            if not faces:
                return {
                    'emotion': None,
                    'suggested_filters': SuggestionEngine.suggest_filters(),
                    'suggested_templates': SuggestionEngine.suggest_templates(),
                    'message': 'No face detected, showing default suggestions'
                }

            # Use largest face
            largest_face = max(faces, key=lambda f: f['bbox'][2] * f['bbox'][3])
            face_region = model_manager.detector.get_face_region(image, largest_face)

            # Detect emotion
            emotion_result = model_manager.detect_emotion(face_region)
            emotion = emotion_result['dominant']

            # For now, age/gender estimation not implemented yet
            age_range = None
            gender = None

            # Get suggestions
            filters = SuggestionEngine.suggest_filters(emotion, age_range, gender)
            templates = SuggestionEngine.suggest_templates(emotion, age_range, gender)

            return {
                'emotion': emotion,
                'emotion_confidence': emotion_result['confidence'],
                'suggested_filters': filters,
                'suggested_templates': templates,
                'message': f'Suggestions based on detected {emotion} emotion'
            }

        except Exception as e:
            # Fallback to defaults
            return {
                'emotion': None,
                'suggested_filters': SuggestionEngine.suggest_filters(),
                'suggested_templates': SuggestionEngine.suggest_templates(),
                'message': f'Analysis failed ({str(e)}), showing default suggestions'
            }


# Singleton instance
_suggestion_engine = None

def get_suggestion_engine():
    """Get singleton SuggestionEngine instance"""
    global _suggestion_engine
    if _suggestion_engine is None:
        _suggestion_engine = SuggestionEngine()
    return _suggestion_engine