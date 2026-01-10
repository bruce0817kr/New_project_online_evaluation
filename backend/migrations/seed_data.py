"""
Initial Seed Data - 초기 데이터 삽입

관리자 계정 및 샘플 데이터 생성
"""
import asyncio
import uuid
from datetime import datetime, date
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.project import Project
from app.models.company import Company
from app.models.evaluation import Evaluation


def seed_database():
    """데이터베이스 초기 데이터 생성"""
    db = SessionLocal()

    try:
        print("🌱 Starting database seeding...")

        # 1. 사용자 생성
        print("\n1️⃣ Creating users...")

        # 관리자 계정
        admin = User(
            id=uuid.uuid4(),
            username="admin",
            email="admin@sme-eval.com",
            hashed_password=hash_password("Admin123!"),
            full_name="시스템 관리자",
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin)
        print(f"   ✅ Admin user created: {admin.username}")

        # 심사위원 계정들
        evaluators = []
        evaluator_data = [
            ("evaluator1", "평가위원1", "evaluator1@sme-eval.com", "Eval123!"),
            ("evaluator2", "평가위원2", "evaluator2@sme-eval.com", "Eval123!"),
            ("evaluator3", "평가위원3", "evaluator3@sme-eval.com", "Eval123!"),
            ("evaluator4", "평가위원4", "evaluator4@sme-eval.com", "Eval123!"),
            ("evaluator5", "평가위원5", "evaluator5@sme-eval.com", "Eval123!"),
        ]

        for username, full_name, email, password in evaluator_data:
            evaluator = User(
                id=uuid.uuid4(),
                username=username,
                email=email,
                hashed_password=hash_password(password),
                full_name=full_name,
                role=UserRole.EVALUATOR,
                is_active=True
            )
            evaluators.append(evaluator)
            db.add(evaluator)
            print(f"   ✅ Evaluator created: {evaluator.username}")

        # 2. 프로젝트 생성
        print("\n2️⃣ Creating project...")

        project = Project(
            id=uuid.uuid4(),
            name="2026년 스마트제조 혁신기술 지원사업",
            description="중소기업의 스마트제조 기술 개발 및 사업화를 지원합니다",
            stage="document",  # document, presentation
            status="in_progress",  # planning, in_progress, completed
            evaluation_template={
                "items": [
                    {
                        "name": "기술성",
                        "weight": 0.4,
                        "max_score": 100,
                        "description": "기술의 혁신성 및 우수성"
                    },
                    {
                        "name": "사업성",
                        "weight": 0.3,
                        "max_score": 100,
                        "description": "사업화 가능성 및 시장성"
                    },
                    {
                        "name": "팀역량",
                        "weight": 0.2,
                        "max_score": 100,
                        "description": "인력 및 조직의 전문성"
                    },
                    {
                        "name": "정책부합성",
                        "weight": 0.1,
                        "max_score": 100,
                        "description": "정책 목표 부합도"
                    }
                ]
            },
            start_date=date(2026, 1, 15),
            end_date=date(2026, 2, 28)
        )
        db.add(project)
        print(f"   ✅ Project created: {project.name}")

        # 3. 회사 생성
        print("\n3️⃣ Creating companies...")

        companies_data = [
            {
                "name": "(주)테크이노베이션",
                "business_number": "123-45-67890",
                "ceo_name": "홍길동",
                "address": "서울특별시 강남구 테헤란로 123",
                "contact_email": "contact@techinno.com",
                "contact_phone": "02-1234-5678"
            },
            {
                "name": "(주)스마트팩토리코리아",
                "business_number": "234-56-78901",
                "ceo_name": "김철수",
                "address": "경기도 성남시 분당구 판교로 456",
                "contact_email": "info@smartfactory.kr",
                "contact_phone": "031-2345-6789"
            },
            {
                "name": "(주)AI솔루션즈",
                "business_number": "345-67-89012",
                "ceo_name": "이영희",
                "address": "대전광역시 유성구 대덕대로 789",
                "contact_email": "hello@aisolutions.kr",
                "contact_phone": "042-3456-7890"
            },
            {
                "name": "(주)그린에너지텍",
                "business_number": "456-78-90123",
                "ceo_name": "박민수",
                "address": "부산광역시 해운대구 센텀중앙로 321",
                "contact_email": "contact@greenenergy.co.kr",
                "contact_phone": "051-4567-8901"
            },
            {
                "name": "(주)바이오메드",
                "business_number": "567-89-01234",
                "ceo_name": "최지혜",
                "address": "인천광역시 연수구 송도과학로 654",
                "contact_email": "info@biomed.kr",
                "contact_phone": "032-5678-9012"
            }
        ]

        companies = []
        for company_data in companies_data:
            company = Company(
                id=uuid.uuid4(),
                project_id=project.id,
                name=company_data["name"],
                business_number=company_data["business_number"],
                ceo_name=company_data["ceo_name"],
                address=company_data["address"],
                contact_email=company_data["contact_email"],
                contact_phone=company_data["contact_phone"],
                ocr_data={
                    "사업자등록번호": company_data["business_number"],
                    "상호": company_data["name"],
                    "대표자": company_data["ceo_name"]
                },
                ocr_confidence=0.95
            )
            companies.append(company)
            db.add(company)
            print(f"   ✅ Company created: {company.name}")

        # 4. 평가 데이터 생성 (각 심사위원이 각 회사를 평가)
        print("\n4️⃣ Creating evaluations...")

        evaluation_count = 0
        for company in companies:
            for evaluator in evaluators:
                # 일부는 제출된 상태, 일부는 작성 중
                is_submitted = evaluation_count % 3 == 0  # 33% 제출 완료

                if is_submitted:
                    # 제출된 평가 (점수 포함)
                    scores_data = {
                        "기술성": 80 + (evaluation_count % 20),
                        "사업성": 75 + (evaluation_count % 25),
                        "팀역량": 85 + (evaluation_count % 15),
                        "정책부합성": 90 + (evaluation_count % 10)
                    }

                    # 가중 평균 계산
                    weights = {"기술성": 0.4, "사업성": 0.3, "팀역량": 0.2, "정책부합성": 0.1}
                    total_score = sum(scores_data[k] * weights[k] for k in scores_data.keys())

                    evaluation = Evaluation(
                        id=uuid.uuid4(),
                        company_id=company.id,
                        evaluator_id=evaluator.id,
                        scores_data=scores_data,
                        overall_comment=f"{company.name}에 대한 {evaluator.full_name}의 종합 의견입니다.",
                        total_score=round(total_score, 2),
                        weighted_score=round(total_score, 2),
                        is_submitted=True,
                        submitted_at=datetime.utcnow(),
                        signature_data="data:image/png;base64,iVBORw0KG..."  # Mock signature
                    )
                else:
                    # 작성 중인 평가 (일부 점수만)
                    evaluation = Evaluation(
                        id=uuid.uuid4(),
                        company_id=company.id,
                        evaluator_id=evaluator.id,
                        scores_data={"기술성": 80},
                        is_submitted=False
                    )

                db.add(evaluation)
                evaluation_count += 1

        print(f"   ✅ {evaluation_count} evaluations created")

        # Commit all changes
        db.commit()

        print("\n✅ Database seeding completed successfully!")
        print("\n📊 Summary:")
        print(f"   - Users: {len(evaluators) + 1} (1 admin + {len(evaluators)} evaluators)")
        print(f"   - Projects: 1")
        print(f"   - Companies: {len(companies)}")
        print(f"   - Evaluations: {evaluation_count}")
        print("\n🔑 Login Credentials:")
        print("   Admin:")
        print("      Username: admin")
        print("      Password: Admin123!")
        print("\n   Evaluators:")
        print("      Username: evaluator1~5")
        print("      Password: Eval123!")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error during seeding: {str(e)}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
