from django.contrib import admin

from qa.models import Answer, Question, Tag, Vote


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    readonly_fields = ("slug",)


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1

    fields = ("content", "author", "is_correct", "created_at")
    readonly_fields = ("created_at",)

    raw_id_fields = ("author",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]

    fieldsets = (
        (None, {"fields": ("id", "author", "title", "slug", "content")}),
        ("Status", {"fields": ("is_answered",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    list_display = ("title", "author", "answer_count", "is_answered", "created_at")
    list_filter = ("created_at", "author")
    search_fields = ("title", "content", "author__login")

    raw_id_fields = ("author",)
    readonly_fields = ("id", "slug", "created_at", "updated_at", "is_answered")

    def answer_count(self, obj):
        return obj.answers.count()

    def is_answered(self, obj):
        return obj.answers.filter(is_correct=True).exists()
    is_answered.boolean = True
    is_answered.short_description = "Correct Answer?"


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("question", "author", "content")}),
        ("Status", {"fields": ("is_correct",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


    list_display = ("question_title", "author", "content_trimmed", "is_correct", "created_at")
    list_filter = ("is_correct", "created_at", "author")
    search_fields = ("body", "user__login", "question__title")

    raw_id_fields = ("question", "author")
    readonly_fields = ("content_trimmed", "created_at", "updated_at")

    def content_trimmed(self, obj):
        return obj.content if len(obj.content) <= 50 else obj.content[:50] + "..."

    def question_title(self, obj):
        return obj.question.title
    question_title.short_description = "Question"


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    raw_id_fields = ("user",)
    readonly_fields = ("created_at", "updated_at")

    list_display = ("user", "type", "target", "created_at")
    list_filter = ("type", "content_type", "created_at")

    search_fields = ("object_id",)

    ordering = ("-created_at",)
