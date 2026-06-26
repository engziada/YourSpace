"""Seed script for YourSpace debug/test database."""
from app import app, db
from app.models import (
    User, Employee, Customer,
    Job, Institute, Space,
    Package, PricingRule, Subscription,
    Log, Post, Comment
)
from passlib.hash import bcrypt
import datetime
import random


def seed_users():
    """Seed users (admin + regular staff + a locked user)."""
    users_data = [
        {
            "username": "admin2", "password": "admin2",
            "is_admin": True, "is_active": True, "is_locked": False
        },
        {
            "username": "manager1", "password": "manager1",
            "is_admin": False, "is_active": True, "is_locked": False
        },
        {
            "username": "staff1", "password": "staff1",
            "is_admin": False, "is_active": True, "is_locked": False
        },
        {
            "username": "staff2", "password": "staff2",
            "is_admin": False, "is_active": True, "is_locked": False
        },
        {
            "username": "inactive_user", "password": "password",
            "is_admin": False, "is_active": False, "is_locked": False
        },
        {
            "username": "locked_user", "password": "password",
            "is_admin": False, "is_active": True, "is_locked": True
        },
    ]
    users = []
    for data in users_data:
        existing = User.query.filter_by(username=data["username"]).first()
        if not existing:
            user = User(
                username=data["username"],
                password_hash=bcrypt.hash(data["password"].encode("utf-8")),
                is_admin=data["is_admin"]
            )
            user.is_active = data["is_active"]
            user.is_locked = data["is_locked"]
            db.session.add(user)
            users.append(user)
    db.session.commit()
    return User.query.all()


def seed_employees():
    """Seed employees linked to users."""
    employees_data = [
        {"username": "admin2", "name": "Ahmed Ziada", "phone": "0500000001",
         "email": "ahmed@yourspace.local", "gender": "1"},
        {"username": "manager1", "name": "Sara Al-Rashid", "phone": "0500000002",
         "email": "sara@yourspace.local", "gender": "2"},
        {"username": "staff1", "name": "Khaled Omar", "phone": "0500000003",
         "email": "khaled@yourspace.local", "gender": "1"},
        {"username": "staff2", "name": "Fatima Noor", "phone": "0500000004",
         "email": "fatima@yourspace.local", "gender": "2"},
        {"username": "inactive_user", "name": "Inactive Employee", "phone": "0500000005",
         "email": "inactive@yourspace.local", "gender": "1"},
        {"username": "locked_user", "name": "Locked Employee", "phone": "0500000006",
         "email": "locked@yourspace.local", "gender": "1"},
    ]
    for data in employees_data:
        if Employee.query.filter_by(phone=data["phone"]).first():
            continue
        user = User.query.filter_by(username=data["username"]).first()
        if not user:
            continue
        if Employee.query.filter_by(user_id=user.id).first():
            continue
        emp = Employee(
            name=data["name"], phone=data["phone"],
            email=data["email"], user=user, gender=data["gender"]
        )
        emp.address = "123 Test Street, Riyadh"
        emp.birthdate = datetime.date(1990 + random.randint(0, 10), random.randint(1, 12), random.randint(1, 28))
        emp.national_id = f"10{random.randint(10000000, 99999999)}"
        db.session.add(emp)
    db.session.commit()
    return Employee.query.all()


def seed_jobs():
    """Seed job categories."""
    job_names = ["Software Engineer", "Designer", "Marketer", "Consultant", "Student"]
    for name in job_names:
        if not Job.query.filter_by(name=name).first():
            db.session.add(Job(name=name))
    db.session.commit()
    return Job.query.all()


def seed_institutes(jobs):
    """Seed institutes linked to jobs."""
    institute_data = [
        ("KAUST", jobs[0]), ("STC", jobs[0]), ("SABIC", jobs[0]),
        ("Freelance", jobs[1]), ("Dubai Design Studio", jobs[1]),
        ("Amazon KSA", jobs[2]), ("PWC", jobs[3]),
        ("King Saud University", jobs[4]), ("Effat University", jobs[4]),
    ]
    for name, job in institute_data:
        if not Institute.query.filter_by(name=name).first():
            db.session.add(Institute(name=name, job_id=job.id))
    db.session.commit()
    return Institute.query.all()


def seed_subscriptions():
    """Seed subscription tiers."""
    subs_data = [
        {"name": "Basic", "hours": 5, "price": 150.00},
        {"name": "Standard", "hours": 20, "price": 500.00},
        {"name": "Premium", "hours": 50, "price": 1000.00},
        {"name": "Flex", "hours": 10, "price": 300.00},
    ]
    for data in subs_data:
        if not Subscription.query.filter_by(name=data["name"]).first():
            sub = Subscription(
                name=data["name"], hours=data["hours"],
                price=data["price"]
            )
            db.session.add(sub)
    db.session.commit()
    return Subscription.query.all()


def seed_packages():
    """Seed packages with pricing rules."""
    packages_data = [
        {"name": "Hot Desk", "description": "Shared workspace, first-come first-served.", "rules": [
            (1, 2, 25.00), (3, 5, 22.00), (6, 10, 20.00), (11, 999, 18.00)]},
        {"name": "Dedicated Desk", "description": "Permanent desk in shared area.", "rules": [
            (1, 5, 35.00), (6, 15, 30.00), (16, 999, 28.00)]},
        {"name": "Private Office", "description": "Fully enclosed private office.", "rules": [
            (1, 4, 80.00), (5, 10, 75.00), (11, 999, 70.00)]},
        {"name": "Meeting Room", "description": "Bookable meeting room by the hour.", "rules": [
            (1, 2, 60.00), (3, 6, 55.00), (7, 999, 50.00)]},
    ]
    for data in packages_data:
        if not Package.query.filter_by(name=data["name"]).first():
            pkg = Package(name=data["name"], description=data["description"])
            db.session.add(pkg)
            db.session.flush()  # Get pkg.id
            for from_h, to_h, rate in data["rules"]:
                db.session.add(PricingRule(
                    from_=from_h, to_=to_h,
                    hourly_rate=rate, package_id=pkg.id
                ))
    db.session.commit()
    return Package.query.all()


def seed_spaces():
    """Seed workspace locations/rooms."""
    spaces_data = [
        {"name": "Zone A - Open Area", "area": "120", "capacity": 20,
         "location": "Building 1, Ground Floor", "description": "Bright open-plan hot desk area."},
        {"name": "Zone B - Quiet Zone", "area": "80", "capacity": 12,
         "location": "Building 1, 1st Floor", "description": "Silent working area with individual pods."},
        {"name": "Meeting Room - Blue", "area": "30", "capacity": 8,
         "location": "Building 2, Ground Floor", "description": "Projector, whiteboard, video conferencing."},
        {"name": "Meeting Room - Green", "area": "25", "capacity": 6,
         "location": "Building 2, Ground Floor", "description": "Screen sharing, whiteboard."},
        {"name": "Private Office - 101", "area": "20", "capacity": 4,
         "location": "Building 1, 2nd Floor", "description": "Small private office for teams up to 4."},
        {"name": "Private Office - 102", "area": "18", "capacity": 3,
         "location": "Building 1, 2nd Floor", "description": "Compact private office."},
        {"name": "Event Hall", "area": "200", "capacity": 100,
         "location": "Building 3, Ground Floor", "description": "Large event and workshop space."},
        {"name": "Podcast Studio", "area": "15", "capacity": 4,
         "location": "Building 3, Basement", "description": "Soundproof studio with mics and mixer."},
    ]
    for data in spaces_data:
        if not Space.query.filter_by(name=data["name"]).first():
            sp = Space(
                name=data["name"], area=data["area"],
                capacity=data["capacity"], location=data["location"],
                description=data["description"], is_ready=True
            )
            db.session.add(sp)
    db.session.commit()
    return Space.query.all()


def seed_customers(users, jobs, institutes, subscriptions):
    """Seed customers with linked user accounts, dates spread across months."""
    customers_data = [
        {"name": "Mohammed Al-Qahtani", "phone": "0551111111",
         "email": "mohammed@example.com", "gender": "1",
         "job": jobs[0], "institute": institutes[0],
         "subscription": subscriptions[1], "month": 1},
        {"name": "Lina Hassan", "phone": "0552222222",
         "email": "lina@example.com", "gender": "2",
         "job": jobs[1], "institute": institutes[3],
         "subscription": subscriptions[0], "month": 1},
        {"name": "Omar Farouk", "phone": "0553333333",
         "email": "omar@example.com", "gender": "1",
         "job": jobs[3], "institute": institutes[6],
         "subscription": subscriptions[2], "month": 2},
        {"name": "Nora Al-Saud", "phone": "0554444444",
         "email": "nora@example.com", "gender": "2",
         "job": jobs[4], "institute": institutes[7],
         "subscription": subscriptions[0], "month": 2},
        {"name": "Yasser Ibrahim", "phone": "0555555555",
         "email": "yasser@example.com", "gender": "1",
         "job": jobs[2], "institute": institutes[5],
         "subscription": subscriptions[3], "month": 3},
        {"name": "Huda Al-Farsi", "phone": "0556666666",
         "email": "huda@example.com", "gender": "2",
         "job": jobs[1], "institute": institutes[4],
         "subscription": subscriptions[2], "month": 3},
        {"name": "Test Customer (No Sub)", "phone": "0557777777",
         "email": "nosub@example.com", "gender": "1",
         "job": jobs[0], "institute": institutes[1],
         "subscription": subscriptions[0], "month": 4},
        {"name": "Faisal Bin-Talal", "phone": "0558888888",
         "email": "faisal@example.com", "gender": "1",
         "job": jobs[0], "institute": institutes[2],
         "subscription": subscriptions[1], "month": 4},
        {"name": "Rania Al-Mutairi", "phone": "0559999999",
         "email": "rania@example.com", "gender": "2",
         "job": jobs[4], "institute": institutes[8],
         "subscription": subscriptions[3], "month": 5},
        {"name": "Tariq Al-Harbi", "phone": "0550000000",
         "email": "tariq@example.com", "gender": "1",
         "job": jobs[3], "institute": institutes[6],
         "subscription": subscriptions[0], "month": 5},
        {"name": "Maha Al-Qarni", "phone": "0551212121",
         "email": "maha@example.com", "gender": "2",
         "job": jobs[1], "institute": institutes[3],
         "subscription": subscriptions[2], "month": 6},
        {"name": "Bandar Al-Shehri", "phone": "0552323232",
         "email": "bandar@example.com", "gender": "1",
         "job": jobs[2], "institute": institutes[5],
         "subscription": subscriptions[1], "month": 6},
    ]
    customers = []
    for i, data in enumerate(customers_data):
        if Customer.query.filter_by(phone=data["phone"]).first():
            continue
        u = User(
            username=f"customer{i+1}",
            password_hash=bcrypt.hash("customer123".encode("utf-8")),
            is_admin=False
        )
        db.session.add(u)
        db.session.flush()
        sub_start = datetime.datetime(2026, data["month"], random.randint(1, 15), 9, 0, 0)
        creation = datetime.datetime(2026, data["month"], random.randint(1, 10), 9, 0, 0)
        cust = Customer(
            name=data["name"], phone=data["phone"],
            email=data["email"], gender=data["gender"],
            user=u, job=data["job"],
            institute=data["institute"],
            subscription=data["subscription"],
            subscription_startdate=sub_start,
            subscription_remaining=data["subscription"].hours,
            creation_date=creation
        )
        db.session.add(cust)
        customers.append(cust)
    db.session.commit()
    return Customer.query.all()


def _make_log(month, day, hour_start, hour_end, period, price,
              space_idx, cust_idx, emp_idx, pkg_idx,
              use_sub=False, active=False):
    """Helper to build a log entry with fixed dates spread across months."""
    start = datetime.datetime(2026, month, day, hour_start, 0, 0)
    end = datetime.datetime(2026, month, day, hour_end, 0, 0) if hour_end else None
    return {
        "start": start, "end": end, "period": period,
        "total_price": price, "space_idx": space_idx,
        "cust_idx": cust_idx, "emp_idx": emp_idx,
        "pkg_idx": pkg_idx, "use_subscription": use_sub,
        "is_active": active
    }


def seed_logs(customers, employees, spaces, packages):
    """Seed booking/usage logs across Jan-Jun 2026 for rich dashboard data."""
    logs_tpl = [
        # Jan 2026
        _make_log(1, 5, 9, 12, "3:00", 75.00, 2, 0, 0, 3),
        _make_log(1, 8, 10, 14, "4:00", 100.00, 4, 1, 1, 2),
        _make_log(1, 12, 13, 15, "2:00", 0.00, 1, 2, 0, 1, use_sub=True),
        _make_log(1, 15, 9, 11, "2:00", 50.00, 3, 3, 2, 3),
        _make_log(1, 20, 14, 18, "4:00", 140.00, 5, 4, 3, 2),
        _make_log(1, 25, 10, 13, "3:00", 66.00, 0, 5, 1, 0),
        # Feb 2026
        _make_log(2, 3, 9, 12, "3:00", 75.00, 2, 6, 0, 3),
        _make_log(2, 7, 10, 16, "6:00", 180.00, 4, 7, 1, 2),
        _make_log(2, 10, 11, 13, "2:00", 0.00, 1, 0, 0, 1, use_sub=True),
        _make_log(2, 14, 9, 10, "1:00", 25.00, 6, 1, 1, 3),
        _make_log(2, 18, 13, 17, "4:00", 140.00, 5, 2, 2, 2),
        _make_log(2, 22, 8, 11, "3:00", 60.00, 3, 3, 3, 0),
        # Mar 2026
        _make_log(3, 2, 9, 13, "4:00", 100.00, 2, 4, 0, 3),
        _make_log(3, 6, 10, 18, "8:00", 160.00, 4, 5, 1, 2),
        _make_log(3, 9, 12, 14, "2:00", 0.00, 1, 6, 0, 1, use_sub=True),
        _make_log(3, 12, 9, 11, "2:00", 50.00, 7, 7, 2, 0),
        _make_log(3, 16, 14, 17, "3:00", 75.00, 0, 0, 3, 3),
        _make_log(3, 20, 11, 15, "4:00", 80.00, 5, 1, 1, 2),
        _make_log(3, 25, 10, 12, "2:00", 44.00, 3, 2, 0, 0),
        # Apr 2026
        _make_log(4, 4, 9, 12, "3:00", 75.00, 2, 3, 0, 3),
        _make_log(4, 8, 10, 14, "4:00", 100.00, 4, 4, 1, 2),
        _make_log(4, 11, 13, 15, "2:00", 0.00, 1, 5, 0, 1, use_sub=True),
        _make_log(4, 14, 9, 11, "2:00", 50.00, 6, 6, 2, 0),
        _make_log(4, 18, 14, 18, "4:00", 140.00, 5, 7, 3, 2),
        _make_log(4, 22, 8, 10, "2:00", 40.00, 0, 0, 1, 0),
        _make_log(4, 26, 11, 14, "3:00", 66.00, 3, 1, 0, 3),
        # May 2026
        _make_log(5, 3, 9, 13, "4:00", 100.00, 2, 2, 0, 3),
        _make_log(5, 7, 10, 16, "6:00", 180.00, 4, 3, 1, 2),
        _make_log(5, 10, 12, 14, "2:00", 0.00, 1, 4, 0, 1, use_sub=True),
        _make_log(5, 13, 9, 12, "3:00", 75.00, 7, 5, 2, 0),
        _make_log(5, 17, 14, 17, "3:00", 75.00, 5, 6, 3, 2),
        _make_log(5, 21, 8, 11, "3:00", 60.00, 0, 7, 1, 3),
        _make_log(5, 25, 10, 13, "3:00", 66.00, 3, 0, 0, 0),
        _make_log(5, 28, 11, 15, "4:00", 80.00, 6, 1, 2, 2),
        # Jun 2026 (active session + recent completed)
        _make_log(6, 5, 9, 12, "3:00", 75.00, 2, 2, 0, 3),
        _make_log(6, 8, 10, 14, "4:00", 100.00, 4, 3, 1, 2),
        _make_log(6, 10, 13, 15, "2:00", 0.00, 1, 4, 0, 1, use_sub=True),
        _make_log(6, 12, 9, 11, "2:00", 50.00, 6, 5, 2, 0),
        _make_log(6, 12, 14, 18, "4:00", 140.00, 5, 6, 3, 2),
        _make_log(6, 13, 10, 13, "3:00", 66.00, 0, 7, 1, 0),
        # One active session (no end time)
        {
            "start": datetime.datetime(2026, 6, 13, 9, 0, 0),
            "end": None, "period": None, "total_price": None,
            "space_idx": 3, "cust_idx": 0, "emp_idx": 0, "pkg_idx": 3,
            "use_subscription": False, "is_active": True
        },
    ]

    for data in logs_tpl:
        log = Log(
            start_time=data["start"],
            end_time=data["end"],
            period=data["period"],
            total_price=data["total_price"],
            space_id=spaces[data["space_idx"]].id,
            customer_id=customers[data["cust_idx"]].id,
            employee_id=employees[data["emp_idx"]].id,
            package_id=packages[data["pkg_idx"]].id,
            use_subscription=data["use_subscription"],
            is_active=data["is_active"]
        )
        db.session.add(log)
    db.session.commit()
    return Log.query.all()


def seed_posts_and_comments():
    """Seed posts and comments for community features."""
    u_admin = User.query.filter_by(username="admin2").first()
    u_mgr = User.query.filter_by(username="manager1").first()
    u_staff1 = User.query.filter_by(username="staff1").first()
    u_staff2 = User.query.filter_by(username="staff2").first()

    posts_data = [
        {"title": "Welcome to YourSpace!",
         "content": "This is the first post on the community board. Feel free to share updates.",
         "user": u_admin},
        {"title": "New Podcast Studio Available",
         "content": "We just opened a soundproof podcast studio in Building 3. Book it today!",
         "user": u_mgr},
        {"title": "Weekend Workshop: UX Design",
         "content": "Join us this Saturday for a hands-on UX design workshop. Seats limited.",
         "user": u_staff1},
    ]
    posts = []
    for data in posts_data:
        if not data["user"]:
            continue
        if not Post.query.filter_by(title=data["title"]).first():
            post = Post(title=data["title"], content=data["content"], user_id=data["user"].id)
            db.session.add(post)
            db.session.flush()
            posts.append(post)
    db.session.commit()

    comments_data = [
        {"content": "Great news! Looking forward to it.", "user": u_staff1, "post_idx": 0},
        {"content": "Can we bring our own equipment?", "user": u_staff2, "post_idx": 1},
        {"content": "Yes, you can bring your own mics.", "user": u_mgr, "post_idx": 1},
        {"content": "Registered! See you Saturday.", "user": u_staff2, "post_idx": 2},
    ]
    for data in comments_data:
        if not data["user"] or data["post_idx"] >= len(posts):
            continue
        comment = Comment(
            content=data["content"],
            user_id=data["user"].id,
            post_id=posts[data["post_idx"]].id
        )
        db.session.add(comment)
    db.session.commit()
    return Post.query.all(), Comment.query.all()


def run_seed():
    """Run all seeders in order."""
    with app.app_context():
        print("Seeding database...")
        users = seed_users()
        print(f"  -> {len(users)} users created")
        employees = seed_employees()
        print(f"  -> {len(employees)} employees created")
        jobs = seed_jobs()
        print(f"  -> {len(jobs)} jobs created")
        institutes = seed_institutes(jobs)
        print(f"  -> {len(institutes)} institutes created")
        subscriptions = seed_subscriptions()
        print(f"  -> {len(subscriptions)} subscriptions created")
        packages = seed_packages()
        print(f"  -> {len(packages)} packages created")
        spaces = seed_spaces()
        print(f"  -> {len(spaces)} spaces created")
        customers = seed_customers(users, jobs, institutes, subscriptions)
        print(f"  -> {len(customers)} customers created")
        logs = seed_logs(customers, employees, spaces, packages)
        print(f"  -> {len(logs)} logs created")
        posts, comments = seed_posts_and_comments()
        print(f"  -> {len(posts)} posts, {len(comments)} comments created")
        print("\nDone! Database seeded successfully.")


if __name__ == "__main__":
    run_seed()
