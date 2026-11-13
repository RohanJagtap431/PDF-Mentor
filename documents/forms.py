
from django import forms
from .models import Document


class DocumentUploadForm(forms.ModelForm):

    pdf_file = forms.FileField(
        label="Select PDF File",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control",
                "accept": ".pdf,application/pdf",
            }
        )
    )

    class Meta:
        model = Document
        fields = [
            "title",
            "description",
            "pdf_file",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter PDF title",
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Enter PDF description",
                "rows": 4,
            }),
        }

    
    def clean_pdf_file(self):
        file = self.cleaned_data["pdf_file"]

        if file.size == 0:
            raise forms.ValidationError("The uploaded file is empty.")

        if not file.name.lower().endswith(".pdf"):
            raise forms.ValidationError("Only PDF files are allowed.")

        file.seek(0)
        signature = file.read(5)
        file.seek(0)

        if signature != b"%PDF-":
            raise forms.ValidationError(
                "Invalid PDF file. Please select a valid PDF."
            )

        return file
    
    

class DocumentEditForm(forms.ModelForm):

    class Meta:
        model = Document
        fields = ["title", "description"]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter PDF title",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Enter PDF description",
                "rows": 4,
            }),
        }

