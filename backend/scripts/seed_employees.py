"""
Seed ~1200 test employees for transport optimization testing.
Run: python backend/scripts/seed_employees.py
"""
import random
import uuid
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import psycopg2
from psycopg2.extras import execute_values

TENANT_ID = "0cea9745-6aa2-4105-9bdc-341d95999048"
DB_URL = "postgresql://postgres:password@helium:5432/heliumdb"

SHIFTS = ["P1", "P2", "P3", "N", "S"]

FIRST_NAMES_M = [
    "Mohammed","Ahmed","Youssef","Ibrahim","Omar","Hassan","Ali","Khalid",
    "Rachid","Mustapha","Hamza","Amine","Karim","Saad","Noureddine",
    "Abdelilah","Zakaria","Hicham","Othmane","Tariq","Adil","Soufiane",
    "Mehdi","Anass","Bilal","Driss","Fouad","Issam","Jawad","Lahcen",
]
FIRST_NAMES_F = [
    "Fatima","Khadija","Amina","Zineb","Nadia","Samira","Hafida","Laila",
    "Souad","Hanane","Imane","Meryem","Naima","Sanaa","Houda","Aicha",
    "Malika","Rajaa","Loubna","Ilham","Ghita","Siham","Wafae","Bouchra",
    "Najat","Soumia","Kawtar","Hasnaa","Latifa","Jamila",
]
LAST_NAMES = [
    "Benali","Benaissa","Benomar","Benkiran","Bennani","Berrada","Chaoui",
    "Chraibi","Dahbi","El Amrani","El Fassi","El Idrissi","El Kabbaj",
    "El Mansouri","El Yazghi","Errahmani","Filali","Hajji","Hassouni",
    "Idrissi","Jaafar","Lahlou","Lamrani","Laroui","Louizi","Maâchi",
    "Mekki","Moumen","Naciri","Ouali","Ouazzani","Qasmi","Rahmani",
    "Sabri","Sahraoui","Senhaji","Skali","Slaoui","Talbi","Tazi",
    "Tijani","Touhami","Wahbi","Yakine","Zemmouri","Zouiten","Bouali",
    "Laaroussi","Khattabi","Mouttaki",
]
FUNCTIONS = [
    "Technicien","Opérateur","Ingénieur","Agent de maîtrise","Superviseur",
    "Analyste","Mécanicien","Électricien","Conducteur","Logisticien",
    "Comptable","Administratif","RH","Sécurité","Qualité",
]
DEPARTMENTS = [
    "Production","Maintenance","Logistique","RH","Finance",
    "Sécurité","Qualité","Informatique","Administration","Transport",
]
TRANSPORT_MODES = ["company_bus","personal_car","taxi","walk","motorcycle"]
CITIES = ["Khouribga","Boujniba","Oued Zem","Boulanoir","Hattane","Gueffaf","Bir Mezoui"]


def random_name():
    gender = random.choice(["M", "F"])
    if gender == "M":
        first = random.choice(FIRST_NAMES_M)
    else:
        first = random.choice(FIRST_NAMES_F)
    last = random.choice(LAST_NAMES)
    return first, last


def jitter(coord, max_delta=0.005):
    return coord + random.uniform(-max_delta, max_delta)


def main():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    cur.execute(
        "SELECT id FROM site WHERE tenant_id=%s ORDER BY code",
        (TENANT_ID,)
    )
    sites = [row[0] for row in cur.fetchall()]
    if not sites:
        print("No sites found! Seed sites first.")
        sys.exit(1)
    print(f"Found {len(sites)} sites")

    cur.execute(
        "SELECT id, lat, lng FROM point_arret WHERE tenant_id=%s",
        (TENANT_ID,)
    )
    stops = cur.fetchall()
    if not stops:
        print("No points d'arrêt found! Seed stops first.")
        sys.exit(1)
    print(f"Found {len(stops)} points d'arrêt")

    cur.execute(
        "DELETE FROM employee WHERE tenant_id=%s AND matricule LIKE 'EMP%%'",
        (TENANT_ID,)
    )
    deleted = cur.rowcount
    print(f"Deleted {deleted} existing EMP* employees")

    TARGET = 1200
    NO_TRANSPORT = 300

    rows = []
    for i in range(1, TARGET + 1):
        emp_id = str(uuid.uuid4())
        matricule = f"EMP{i:05d}"
        first_name, last_name = random_name()

        site_id = sites[i % len(sites)]
        shift = SHIFTS[i % len(SHIFTS)]

        stop = random.choice(stops)
        stop_id, stop_lat, stop_lng = stop
        lat = round(jitter(float(stop_lat), 0.004), 7)
        lng = round(jitter(float(stop_lng), 0.004), 7)

        is_no_transport = i <= NO_TRANSPORT
        transport_required = not is_no_transport
        has_private_car = is_no_transport
        opt_in = "Oui" if (not is_no_transport and random.random() > 0.05) else "Non"
        if is_no_transport:
            current_mode = random.choice(["personal_car","taxi","motorcycle","walk"])
            point_arret_id = None
        else:
            current_mode = "company_bus"
            point_arret_id = stop_id

        is_pmr = random.random() < 0.04
        phone = f"+2126{random.randint(10000000,99999999)}"
        function_role = random.choice(FUNCTIONS)
        department = random.choice(DEPARTMENTS)
        city = random.choice(CITIES)
        quartier = f"Quartier {random.choice(['Al Amal','Al Wifaq','Hassania','Medersa','Centre','Hay Mohammadi','Hay Salam','Anassi','Tamaris'])}"
        address = f"{random.randint(1,200)} Rue {random.choice(['Hassan II','Mohammed V','de la Paix','Atlas','Ifrane','Al Massira','des Orangers'])}"

        rows.append((
            emp_id, TENANT_ID, matricule, first_name, last_name,
            site_id, shift, lat, lng, address, quartier, city,
            is_pmr, transport_required, current_mode, opt_in,
            has_private_car, function_role, department, phone,
            point_arret_id,
        ))

    execute_values(
        cur,
        """
        INSERT INTO employee (
            id, tenant_id, matricule, first_name, last_name,
            site_id, shift_time, lat, lng, address, quartier, city,
            is_pmr, transport_required, current_transport_mode, opt_in_company_transport,
            has_private_car, function_role, department, phone,
            point_arret_id
        ) VALUES %s
        ON CONFLICT (tenant_id, matricule) DO NOTHING
        """,
        rows,
    )
    inserted = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {inserted} employees ({NO_TRANSPORT} without company transport, {TARGET - NO_TRANSPORT} using company transport).")
    print("Done!")


if __name__ == "__main__":
    main()
