"""Seed des catégories de services — marché algérien."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.category import Category

DEFAULT_CATEGORIES = [
    ("dev-web-mobile", "Développement web & mobile", "Web & mobile development", "تطوير الويب والجوال", 1),
    ("design-graphique", "Design graphique & identité visuelle", "Graphic design & branding", "التصميم الجرافيكي والهوية البصرية", 2),
    ("community-management", "Community management & réseaux sociaux", "Community management & social media", "إدارة المجتمع ووسائل التواصل", 3),
    ("redaction-traduction", "Rédaction & traduction (arabe / français / anglais)", "Writing & translation (AR/FR/EN)", "الكتابة والترجمة", 4),
    ("marketing-digital", "Marketing digital & publicité en ligne", "Digital marketing & online ads", "التسويق الرقمي والإعلانات", 5),
    ("montage-video", "Montage vidéo & production de contenu", "Video editing & content production", "مونتاج الفيديو وإنتاج المحتوى", 6),
    ("comptabilite-conseil", "Comptabilité & conseil pour petites entreprises", "Accounting & SME consulting", "المحاسبة والاستشارات للمؤسسات الصغيرة", 7),
    ("photographie", "Photographie", "Photography", "التصوير الفوتوغرافي", 8),
    ("e-commerce", "E-commerce (création et gestion de boutique en ligne)", "E-commerce store setup & management", "التجارة الإلكترونية", 9),
]


def seed() -> None:
    db = SessionLocal()
    try:
        for slug, fr, en, ar, order in DEFAULT_CATEGORIES:
            exists = db.scalar(select(Category).where(Category.slug == slug))
            if exists:
                continue
            db.add(
                Category(
                    slug=slug,
                    name_fr=fr,
                    name_en=en,
                    name_ar=ar,
                    sort_order=order,
                    is_active=True,
                )
            )
        db.commit()
        print("Catégories seedées avec succès.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
