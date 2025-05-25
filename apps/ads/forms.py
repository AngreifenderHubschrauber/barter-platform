from django import forms
from .models import Ad, ExchangeProposal


class AdForm(forms.ModelForm):
    """Форма для создания и редактирования объявлений"""
    
    class Meta:
        model = Ad
        fields = ['title', 'description', 'image_url', 'category', 'condition']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите заголовок объявления'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Опишите ваш товар'
            }),
            'image_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/image.jpg (необязательно)'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'condition': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'title': 'Заголовок',
            'description': 'Описание',
            'image_url': 'URL изображения',
            'category': 'Категория',
            'condition': 'Состояние',
        }
    
    def clean_title(self):
        """Валидация заголовка"""
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise forms.ValidationError('Заголовок должен содержать минимум 5 символов')
        return title
    
    def clean_description(self):
        """Валидация описания"""
        description = self.cleaned_data.get('description')
        if len(description) < 20:
            raise forms.ValidationError('Описание должно содержать минимум 20 символов')
        return description


class ExchangeProposalForm(forms.ModelForm):
    """Форма для создания предложения обмена"""
    
    class Meta:
        model = ExchangeProposal
        fields = ['ad_sender', 'comment']
        widgets = {
            'ad_sender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Напишите комментарий к предложению обмена'
            }),
        }
        labels = {
            'ad_sender': 'Выберите ваше объявление для обмена',
            'comment': 'Комментарий',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Показывать только активные объявления пользователя
            self.fields['ad_sender'].queryset = Ad.objects.filter(
                user=user, 
                is_active=True
            )
    
    def clean_comment(self):
        """Валидация комментария"""
        comment = self.cleaned_data.get('comment')
        if len(comment) < 10:
            raise forms.ValidationError('Комментарий должен содержать минимум 10 символов')
        return comment


class SearchForm(forms.Form):
    """Форма поиска объявлений"""
    
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск по заголовку и описанию...'
        }),
        label='Поиск'
    )
    category = forms.ChoiceField(
        required=False,
        choices=[('', 'Все категории')] + Ad.CATEGORY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Категория'
    )
    condition = forms.ChoiceField(
        required=False,
        choices=[('', 'Любое состояние')] + Ad.CONDITION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Состояние'
    )