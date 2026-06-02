from django.db import models
from django.db.models import UniqueConstraint
from django.core.exceptions import ValidationError


class WireShape(models.TextChoices):
    FLAT = "flat", "Flat"
    ROUND = "round", "Round"


class WireStatus(models.TextChoices):
    IN_STOCK = "in_stock", "In Stock"
    RESERVED = "reserved", "Reserved"
    USED = "used", "Used"
    SCRAP = "scrap", "Scrap"


class WireType(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Назва типу")

    class Meta:
        db_table = "wire_type"
        verbose_name = "Тип дроту/кабелю"
        verbose_name_plural = "Типи дротів та кабелів"

    def __str__(self):
        return self.name


class Manufacturer(models.Model):
    name = models.CharField(max_length=120, unique=True, verbose_name="Виробник")

    class Meta:
        db_table = "manufacturer"
        verbose_name = "Виробник"
        verbose_name_plural = "Виробники"

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=30, unique=True, verbose_name="Колір")

    class Meta:
        db_table = "color"
        verbose_name = "Колір"
        verbose_name_plural = "Кольори"

    def save(self, *args, **kwargs):
        #Прибирає випадкові пробіли та робить першу літеру великою
        if self.name:
            self.name = self.name.strip().capitalize()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class WireTypeColor(models.Model):
    """Таблиця правило: визначає, які кольори дозволені для конкретного типу дроту"""
    wire_type = models.ForeignKey(
        WireType, on_delete=models.CASCADE, related_name="available_colors", verbose_name="Тип дроту"
    )
    color = models.ForeignKey(
        Color, on_delete=models.CASCADE, related_name="wire_types", verbose_name="Дозволений колір"
    )

    class Meta:
        db_table = "wire_type_color"
        constraints = [
            UniqueConstraint(
                fields=["wire_type", "color"],
                name="uq_wire_type_color")
        ]
        verbose_name = "Правило кольору для типу дроту"
        verbose_name_plural = "Правила кольорів для типів проводів"

    def __str__(self):
        return f"{self.wire_type} => {self.color}"


class WireVariant(models.Model):
    wire_type = models.ForeignKey(
        WireType, on_delete=models.PROTECT, related_name="variants",verbose_name="Тип дроту"
    )
    cores = models.PositiveSmallIntegerField(verbose_name="Кількість жил")
    mm2 = models.DecimalField(max_digits=6, decimal_places=2,verbose_name="Переріз (мм.кв)")
    shape = models.CharField(max_length=10, choices=WireShape.choices, verbose_name="Форма")
    manufacturer = models.ForeignKey(
        Manufacturer, on_delete=models.PROTECT, related_name="variants", verbose_name="Виробник"
    )
    color = models.ForeignKey(Color, on_delete=models.PROTECT, related_name="variants",
                              blank=True, null=True, verbose_name="Колір")

    class Meta:
        db_table = "wire_variant"
        constraints = [
            UniqueConstraint(
                fields=["wire_type", "cores", "mm2", "shape", "manufacturer", "color"],
                name="uq_cable_variant",
            )
        ]
        verbose_name = "Варіант дроту"
        verbose_name_plural = "Варіанти дротів"
    
    def clean(self):
        super().clean()

        if hasattr(self, 'wire_type'):
            #Дізнаємося ID всіх дозволених кольорів для нашого типу дроту з таблиці правил
            allowed_colors_ids = WireTypeColor.objects.filter(
                wire_type = self.wire_type
            ).values_list('color_id', flat=True)

            if not allowed_colors_ids.exists():
                #Ситуація 1: в правилах для цього дроту порожньо (наприклад, ВВГ) -> дріт має бути БЕЗКОЛІРНИМ
                if self.color is not None:
                    raise ValidationError({'color':f"Для типу дроту '{self.wire_type}' колір не передбачений. Залиште це поле порожнім."})
            
            else:
                #Ситуація 2: в правилах є кольори (наприклад ПВ-3 або ПВС) -> колір ОБОВ'ЯЗКОВИЙ
                if self.color is None:
                    raise ValidationError({'color':f"Для типу дроту '{self.wire_type}' обов'язково потрібно обарти колір."})
                
                #Перевіряємо, чи обраний колір входить у список дозволених правил
                if self.color_id not in allowed_colors_ids:
                    valid_colors_names = ", ".join(
                        Color.objects.filter(id__in=allowed_colors_ids).values_list('name', flat=True)
                    )
                    raise ValidationError({
                        'color': f"Колір '{self.color}' не дозволений для '{self.wire_type}'. "
                        f"Дозволені варіанти: {valid_colors_names}"
                    })
            

    def __str__(self):
        color_str = f" ({self.color.name})" if self.color else ""
        return f"{self.wire_type} {self.cores} x {self.mm2}{color_str} - {self.manufacturer}"


class WirePiece(models.Model):
    """Облік конкретних фізичних шматків дротів на складі"""
    wire_variant = models.ForeignKey(
        WireVariant, on_delete=models.CASCADE, related_name="pieces", verbose_name="Варіант дроту"
    )
    length_m = models.DecimalField(max_digits=6, decimal_places=1, verbose_name="Довжина (м)")
    location = models.CharField(max_length=60, blank=True, null=True, verbose_name="Місце зберігання")
    status = models.CharField(
        max_length=20, choices=WireStatus.choices, default=WireStatus.IN_STOCK, verbose_name="Статус"
    )
    note = models.TextField(blank=True, default="", verbose_name="Нотатка")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата додавання")

    class Meta:
        db_table = "wire_piece"
        verbose_name = "Фізичний шматок дроту/проводу"
        verbose_name_plural = "Фізичні шматки дротів/проводів"

    def __str__(self):
        return f"{self.wire_variant} / {self.length_m}m"
