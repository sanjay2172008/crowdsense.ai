from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from ultralytics import YOLO
import cv2, numpy as np, os, base64, random, time, json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "crowdsenseai_secret_2024"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Find images folder ────────────────────────────────────────
def find_images_dir():
    candidates = [
        os.path.join(BASE_DIR, "images"),
        os.path.join(os.path.dirname(BASE_DIR), "images"),
        "/opt/render/project/src/images",
        "/opt/render/project/src/crowdsense_ai/images",
    ]
    for p in candidates:
        p = os.path.normpath(p)
        if os.path.isdir(p): return p
    for root_dir in [BASE_DIR, os.path.dirname(BASE_DIR), os.getcwd()]:
        for root, dirs, files in os.walk(root_dir):
            if "meenakshi.jpg" in files or "12b.jpg" in files:
                return root
    return os.path.join(BASE_DIR, "images")

IMG_DIR = find_images_dir()
model   = YOLO("yolov8n.pt")

# ── Demo users (email: password) ─────────────────────────────
USERS = {
    "admin@crowdsense.ai": "admin123",
    "demo@crowdsense.ai":  "demo123",
}

# ═══════════════════════════════════════════════════════════════
#  MTC CHENNAI BUS DATA (70+ routes)
# ═══════════════════════════════════════════════════════════════
BUS_DATA = {
    "1":    {"label":"1",    "route":"Thiruvanmiyur → Broadway",           "destination":"Broadway",         "capacity":80,  "schedule":["5:00","5:30","6:00","6:30","7:00","7:30","8:00","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00","21:30","22:00"]},
    "1a":   {"label":"1A",   "route":"Thiruvanmiyur → Park Town",          "destination":"Park Town",        "capacity":80,  "schedule":["5:15","5:45","6:15","6:45","7:15","7:45","8:15","8:45","9:15","9:45","10:15","10:45","11:15","11:45","12:15","12:45","13:15","13:45","14:15","14:45","15:15","15:45","16:15","16:45","17:15","17:45","18:15","18:45","19:15","19:45","20:15","20:45","21:15","21:45","22:15"]},
    "2":    {"label":"2",    "route":"Adyar → Broadway",                   "destination":"Broadway",         "capacity":80,  "schedule":["5:00","5:20","5:40","6:00","6:20","6:40","7:00","7:20","7:40","8:00","8:20","8:40","9:00","9:20","9:40","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00","21:30","22:00"]},
    "5":    {"label":"5",    "route":"Thiruvanmiyur → Koyambedu",          "destination":"Koyambedu",        "capacity":80,  "schedule":["5:00","5:30","6:00","6:30","7:00","7:15","7:30","7:45","8:00","8:15","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:15","17:30","17:45","18:00","18:30","19:00","19:30","20:00","20:30","21:00","21:30","22:00"]},
    "5b":   {"label":"5B",   "route":"Sholinganallur → Koyambedu",         "destination":"Koyambedu",        "capacity":80,  "schedule":["6:00","6:30","7:00","7:30","8:00","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00","21:30"]},
    "9":    {"label":"9",    "route":"Thiruvanmiyur → Central Station",    "destination":"Central Station",  "capacity":80,  "schedule":["5:00","5:30","6:00","6:30","7:00","7:30","8:00","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00","21:30","22:00"]},
    "10":   {"label":"10",   "route":"Thiruvanmiyur → T.Nagar",            "destination":"T.Nagar",          "capacity":80,  "schedule":["5:00","5:30","6:00","6:15","6:30","6:45","7:00","7:15","7:30","7:45","8:00","8:15","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00","21:30"]},
    "10b":  {"label":"10B",  "route":"Sholinganallur → T.Nagar",           "destination":"T.Nagar",          "capacity":80,  "schedule":["6:00","6:30","7:00","7:30","8:00","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","13:00","14:00","15:00","16:00","17:00","18:00","19:00","20:00","21:00"]},
    "11":   {"label":"11",   "route":"Thiruvanmiyur → Villivakkam",        "destination":"Villivakkam",      "capacity":80,  "schedule":["5:30","6:00","6:30","7:00","7:30","8:00","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00"]},
    "12b":  {"label":"12B",  "route":"Thiruvanmiyur → Broadway",           "destination":"Broadway",         "capacity":80,  "schedule":["5:00","5:20","5:40","6:00","6:20","6:40","7:00","7:20","7:40","8:00","8:20","8:40","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00","21:30","22:00"]},
    "15b":  {"label":"15B",  "route":"Adyar → Koyambedu",                  "destination":"Koyambedu",        "capacity":80,  "schedule":["5:30","6:00","6:30","7:00","7:30","8:00","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00"]},
    "17":   {"label":"17",   "route":"Anna Nagar → Broadway",              "destination":"Broadway",         "capacity":80,  "schedule":["5:00","5:30","6:00","6:30","7:00","7:30","8:00","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00","21:30"]},
    "18":   {"label":"18",   "route":"Velachery → Broadway",               "destination":"Broadway",         "capacity":80,  "schedule":["5:00","5:30","6:00","6:30","7:00","7:30","8:00","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00"]},
    "19":   {"label":"19",   "route":"Tambaram → Broadway",                "destination":"Broadway",         "capacity":80,  "schedule":["5:00","5:30","6:00","6:30","7:00","7:30","8:00","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00","21:30"]},
    "21g":  {"label":"21G",  "route":"Adyar → Koyambedu",                  "destination":"Koyambedu",        "capacity":80,  "schedule":["5:00","5:30","6:00","6:30","7:00","7:30","8:00","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00"]},
    "23":   {"label":"23",   "route":"Guindy → Broadway",                  "destination":"Broadway",         "capacity":80,  "schedule":["5:30","6:00","6:30","7:00","7:30","8:00","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00"]},
    "27":   {"label":"27",   "route":"Chromepet → Broadway",               "destination":"Broadway",         "capacity":80,  "schedule":["5:00","5:30","6:00","6:30","7:00","7:30","8:00","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00","21:30"]},
    "29c":  {"label":"29C",  "route":"Tambaram → Chennai Central",         "destination":"Chennai Central",  "capacity":80,  "schedule":["5:00","5:30","6:00","6:30","7:00","7:30","8:00","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00","21:30","22:00"]},
    "32":   {"label":"32",   "route":"Ambattur → Broadway",                "destination":"Broadway",         "capacity":80,  "schedule":["5:30","6:00","6:30","7:00","7:30","8:00","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00"]},
    "36":   {"label":"36",   "route":"Poonamallee → Broadway",             "destination":"Broadway",         "capacity":80,  "schedule":["5:00","5:30","6:00","6:30","7:00","7:30","8:00","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00","21:30"]},
    "40":   {"label":"40",   "route":"Avadi → Broadway",                   "destination":"Broadway",         "capacity":80,  "schedule":["5:30","6:00","6:30","7:00","7:30","8:00","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00"]},
    "42":   {"label":"42",   "route":"Ennore → Broadway",                  "destination":"Broadway",         "capacity":80,  "schedule":["5:00","5:30","6:00","6:30","7:00","7:30","8:00","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00"]},
    "47":   {"label":"47",   "route":"Thiruvottiyur → Broadway",           "destination":"Broadway",         "capacity":80,  "schedule":["5:00","5:30","6:00","6:30","7:00","7:30","8:00","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00"]},
    "51":   {"label":"51",   "route":"Velachery → Koyambedu",              "destination":"Koyambedu",        "capacity":80,  "schedule":["5:30","6:00","6:30","7:00","7:30","8:00","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00"]},
    "70":   {"label":"70",   "route":"Perambur → Guindy",                  "destination":"Guindy",           "capacity":80,  "schedule":["5:30","6:00","6:30","7:00","7:30","8:00","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00"]},
    "99":   {"label":"99",   "route":"Anna Nagar → Tambaram",              "destination":"Tambaram",         "capacity":80,  "schedule":["5:00","5:30","6:00","6:30","7:00","7:30","8:00","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00","21:30"]},
    "100":  {"label":"100",  "route":"Koyambedu → Airport",                "destination":"Airport",          "capacity":80,  "schedule":["5:00","5:30","6:00","6:30","7:00","7:30","8:00","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00","21:30","22:00"]},
    "108":  {"label":"108",  "route":"Central Station → Airport",          "destination":"Airport",          "capacity":80,  "schedule":["5:00","6:00","7:00","8:00","9:00","10:00","11:00","12:00","13:00","14:00","15:00","16:00","17:00","18:00","19:00","20:00","21:00","22:00"]},
    "142":  {"label":"142",  "route":"Anna Nagar → T.Nagar",               "destination":"T.Nagar",          "capacity":60,  "schedule":["5:00","5:30","6:00","6:30","7:00","7:15","7:30","7:45","8:00","8:15","8:30","8:45","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00","21:30"]},
    "170":  {"label":"170",  "route":"Broadway → Mahabalipuram",           "destination":"Mahabalipuram",    "capacity":60,  "schedule":["6:00","7:00","8:00","9:00","10:00","11:00","12:00","13:00","14:00","15:00","16:00","17:00","18:00","19:00","20:00"]},
    "500":  {"label":"500",  "route":"Koyambedu → Tambaram (AC)",          "destination":"Tambaram",         "capacity":45,  "schedule":["6:00","6:30","7:00","7:30","8:00","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00"]},
    "600":  {"label":"600",  "route":"Koyambedu → Sholinganallur (AC)",    "destination":"Sholinganallur",   "capacity":45,  "schedule":["6:00","6:30","7:00","7:30","8:00","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00"]},
    "700":  {"label":"700",  "route":"Koyambedu → Anna Nagar (AC)",        "destination":"Anna Nagar",       "capacity":45,  "schedule":["6:00","7:00","8:00","9:00","10:00","11:00","12:00","13:00","14:00","15:00","16:00","17:00","18:00","19:00","20:00","21:00"]},
}

# ═══════════════════════════════════════════════════════════════
#  CHENNAI HOSPITALS (25+)
# ═══════════════════════════════════════════════════════════════
HOSPITAL_DATA = {
    "appolo":       {"label":"Apollo Hospitals",                   "location":"Greams Road, Chennai",       "type":"Multi-Specialty", "best_time":"2:00 PM – 4:00 PM",   "capacity":500},
    "mgm":          {"label":"MGM Healthcare",                     "location":"Nelson Manickam Road",       "type":"Multi-Specialty", "best_time":"10:00 AM – 12:00 PM",  "capacity":400},
    "fortis":       {"label":"Fortis Malar Hospital",              "location":"Adyar, Chennai",             "type":"Multi-Specialty", "best_time":"11:00 AM – 1:00 PM",   "capacity":350},
    "meridian":     {"label":"Meridian Hospital",                  "location":"Anna Nagar, Chennai",        "type":"General",         "best_time":"11:00 AM – 1:00 PM",   "capacity":200},
    "rajiv":        {"label":"Rajiv Gandhi Govt. Hospital",        "location":"Park Town, Chennai",         "type":"Government",      "best_time":"6:00 AM – 8:00 AM",    "capacity":1000},
    "stanley":      {"label":"Stanley Medical College Hospital",   "location":"Old Jail Road, Chennai",     "type":"Government",      "best_time":"6:00 AM – 8:00 AM",    "capacity":1500},
    "gggh":         {"label":"Govt. General Hospital Chennai",     "location":"Park Town, Chennai",         "type":"Government",      "best_time":"5:00 AM – 7:00 AM",    "capacity":2000},
    "kmch":         {"label":"Kauvery Medical Centre",             "location":"Alwarpet, Chennai",          "type":"Multi-Specialty", "best_time":"9:00 AM – 11:00 AM",   "capacity":300},
    "vijaya":       {"label":"Vijaya Hospital",                    "location":"NSK Salai, Vadapalani",      "type":"Multi-Specialty", "best_time":"10:00 AM – 12:00 PM",  "capacity":350},
    "miot":         {"label":"MIOT International Hospital",        "location":"Manapakkam, Chennai",        "type":"Multi-Specialty", "best_time":"9:00 AM – 11:00 AM",   "capacity":400},
    "srm":          {"label":"SRM Hospitals",                      "location":"Potheri, Kattankulathur",    "type":"Multi-Specialty", "best_time":"10:00 AM – 12:00 PM",  "capacity":300},
    "sims":         {"label":"SIMS Hospital",                      "location":"Vadapalani, Chennai",        "type":"Multi-Specialty", "best_time":"11:00 AM – 1:00 PM",   "capacity":350},
    "saveetha":     {"label":"Saveetha Medical College",           "location":"Thandalam, Chennai",         "type":"Medical College",  "best_time":"8:00 AM – 10:00 AM",   "capacity":400},
    "cmc":          {"label":"Christian Medical College",          "location":"Vellore (near Chennai)",     "type":"Multi-Specialty", "best_time":"7:00 AM – 9:00 AM",    "capacity":600},
    "madras_eye":   {"label":"Madras Eye Hospital",                "location":"Park Town, Chennai",         "type":"Specialty",       "best_time":"8:00 AM – 10:00 AM",   "capacity":150},
    "sankara":      {"label":"Sankara Nethralaya",                 "location":"Nungambakkam, Chennai",      "type":"Eye Specialty",   "best_time":"8:00 AM – 10:00 AM",   "capacity":200},
    "kanchi":       {"label":"Kanchipuram Govt. Hospital",         "location":"Kanchipuram",                "type":"Government",      "best_time":"6:00 AM – 8:00 AM",    "capacity":500},
    "esi":          {"label":"ESI Hospital Ashok Nagar",           "location":"Ashok Nagar, Chennai",       "type":"Government",      "best_time":"8:00 AM – 10:00 AM",   "capacity":300},
    "kilpauk":      {"label":"Kilpauk Medical College Hospital",   "location":"Kilpauk, Chennai",           "type":"Government",      "best_time":"6:00 AM – 8:00 AM",    "capacity":800},
    "royapettah":   {"label":"Royapettah Govt. Hospital",          "location":"Royapettah, Chennai",        "type":"Government",      "best_time":"7:00 AM – 9:00 AM",    "capacity":600},
    "panimalar":    {"label":"Panimalar Medical College",          "location":"Poonamallee, Chennai",       "type":"Medical College",  "best_time":"9:00 AM – 11:00 AM",   "capacity":350},
    "cri":          {"label":"Cancer Institute (WIA)",             "location":"Adyar, Chennai",             "type":"Cancer Specialty", "best_time":"8:00 AM – 10:00 AM",   "capacity":400},
    "omandurar":    {"label":"Omandurar Govt. Medical College",    "location":"Triplicane, Chennai",        "type":"Government",      "best_time":"6:00 AM – 8:00 AM",    "capacity":700},
    "mmh":          {"label":"Madras Medical Mission",             "location":"Mogappair, Chennai",         "type":"Multi-Specialty", "best_time":"9:00 AM – 11:00 AM",   "capacity":300},
    "iyer":         {"label":"Dr. Mehta's Hospital",               "location":"Chetpet, Chennai",           "type":"Multi-Specialty", "best_time":"10:00 AM – 12:00 PM",  "capacity":250},
}

# ═══════════════════════════════════════════════════════════════
#  FAMOUS TAMIL NADU TEMPLES (30+)
# ═══════════════════════════════════════════════════════════════
TEMPLE_DATA = {
    "meenakshi":       {"label":"Meenakshi Amman Temple",          "location":"Madurai",              "deity":"Goddess Meenakshi",    "best_time":"6:00 AM – 8:00 AM",  "capacity":5000},
    "ramanathaswamy":  {"label":"Ramanathaswamy Temple",           "location":"Rameswaram",           "deity":"Lord Shiva",           "best_time":"5:00 AM – 7:00 AM",  "capacity":4000},
    "palani":          {"label":"Palani Murugan Temple",           "location":"Palani, Dindigul",     "deity":"Lord Murugan",         "best_time":"5:00 AM – 7:00 AM",  "capacity":3000},
    "brihadeeswara":   {"label":"Brihadeeswarar Temple",           "location":"Thanjavur",            "deity":"Lord Shiva",           "best_time":"6:00 AM – 8:00 AM",  "capacity":3000},
    "thiruchendur":    {"label":"Thiruchendur Murugan Temple",     "location":"Thiruchendur",         "deity":"Lord Murugan",         "best_time":"5:00 AM – 7:00 AM",  "capacity":4000},
    "kanchipuram":     {"label":"Kamakshi Amman Temple",           "location":"Kanchipuram",          "deity":"Goddess Kamakshi",     "best_time":"6:00 AM – 8:00 AM",  "capacity":3000},
    "ekambareswarar":  {"label":"Ekambareswarar Temple",           "location":"Kanchipuram",          "deity":"Lord Shiva",           "best_time":"6:00 AM – 8:00 AM",  "capacity":2500},
    "kapaleeshwarar":  {"label":"Kapaleeshwarar Temple",           "location":"Mylapore, Chennai",    "deity":"Lord Shiva",           "best_time":"6:00 AM – 8:00 AM",  "capacity":2000},
    "parthasarathy":   {"label":"Parthasarathy Temple",            "location":"Triplicane, Chennai",  "deity":"Lord Vishnu",          "best_time":"7:00 AM – 9:00 AM",  "capacity":1500},
    "ashtalakshmi":    {"label":"Ashtalakshmi Temple",             "location":"Besant Nagar, Chennai","deity":"Goddess Lakshmi",      "best_time":"6:00 AM – 8:00 AM",  "capacity":1000},
    "vadapalani":      {"label":"Vadapalani Murugan Temple",       "location":"Vadapalani, Chennai",  "deity":"Lord Murugan",         "best_time":"6:00 AM – 8:00 AM",  "capacity":2000},
    "marundeeswarar":  {"label":"Marundeeswarar Temple",           "location":"Thiruvanmiyur, Chennai","deity":"Lord Shiva",          "best_time":"6:00 AM – 8:00 AM",  "capacity":1500},
    "arulmigu_subramanya": {"label":"Tiruttani Murugan Temple",   "location":"Tiruttani",            "deity":"Lord Murugan",         "best_time":"5:00 AM – 7:00 AM",  "capacity":4000},
    "srirangam":       {"label":"Ranganathaswamy Temple",          "location":"Srirangam, Trichy",    "deity":"Lord Vishnu",          "best_time":"6:00 AM – 8:00 AM",  "capacity":6000},
    "chidambaram":     {"label":"Nataraja Temple",                 "location":"Chidambaram",          "deity":"Lord Nataraja",        "best_time":"6:00 AM – 8:00 AM",  "capacity":3000},
    "tirupati":        {"label":"Tirupati Balaji (nearby TN)",     "location":"Tirupati (AP border)", "deity":"Lord Venkateswara",    "best_time":"4:00 AM – 6:00 AM",  "capacity":10000},
    "kanyakumari":     {"label":"Kanyakumari Amman Temple",        "location":"Kanyakumari",          "deity":"Goddess Bhagavathi",   "best_time":"5:00 AM – 7:00 AM",  "capacity":3000},
    "madurai_koodal":  {"label":"Koodal Azhagar Temple",           "location":"Madurai",              "deity":"Lord Vishnu",          "best_time":"7:00 AM – 9:00 AM",  "capacity":2000},
    "uchipillaiyar":   {"label":"Rock Fort Ucchi Pillayar Temple", "location":"Trichy",               "deity":"Lord Ganesha",         "best_time":"6:00 AM – 8:00 AM",  "capacity":2000},
    "thillai_nataraj": {"label":"Thillai Nataraja Temple",         "location":"Chidambaram",          "deity":"Lord Shiva",           "best_time":"6:00 AM – 8:00 AM",  "capacity":2500},
    "nataraj_velankanni": {"label":"Velankanni Church (Basilica)", "location":"Velankanni, Nagapattinam","deity":"Mother Mary",       "best_time":"6:00 AM – 8:00 AM",  "capacity":10000},
    "murugan_swamimalai": {"label":"Swamimalai Murugan Temple",   "location":"Swamimalai, Kumbakonam","deity":"Lord Murugan",        "best_time":"6:00 AM – 8:00 AM",  "capacity":2000},
    "airavatesvara":   {"label":"Airavatesvara Temple",            "location":"Darasuram, Kumbakonam","deity":"Lord Shiva",           "best_time":"7:00 AM – 9:00 AM",  "capacity":1500},
    "gangaikonda":     {"label":"Gangaikonda Cholapuram Temple",   "location":"Gangaikonda Cholapuram","deity":"Lord Shiva",          "best_time":"7:00 AM – 9:00 AM",  "capacity":1500},
    "nellaiappar":     {"label":"Nellaiappar Temple",              "location":"Tirunelveli",          "deity":"Lord Shiva",           "best_time":"6:00 AM – 8:00 AM",  "capacity":2000},
    "kasi_viswanathar":{"label":"Kasi Viswanathar Temple",         "location":"Tenkasi",              "deity":"Lord Shiva",           "best_time":"6:00 AM – 8:00 AM",  "capacity":1500},
    "thiruvengadu":    {"label":"Thiruvengadu Shiva Temple",       "location":"Thiruvengadu",         "deity":"Lord Shiva",           "best_time":"6:00 AM – 8:00 AM",  "capacity":1000},
    "pichavaram":      {"label":"Shiva Temple Pichavaram",         "location":"Pichavaram, Chidambaram","deity":"Lord Shiva",         "best_time":"7:00 AM – 9:00 AM",  "capacity":800},
    "vaidyamahalingam":{"label":"Vaidyamahalingam Temple",         "location":"Sirkazhi",             "deity":"Lord Shiva",           "best_time":"6:00 AM – 8:00 AM",  "capacity":1000},
    "subramaniaswamy": {"label":"Subramaniaswamy Temple",          "location":"Tiruchendur",          "deity":"Lord Murugan",         "best_time":"5:00 AM – 7:00 AM",  "capacity":3500},
}

ALL_DATA = {}
for k,v in BUS_DATA.items():      ALL_DATA[k] = {**v, "category":"bus"}
for k,v in HOSPITAL_DATA.items(): ALL_DATA[k] = {**v, "category":"hospital"}
for k,v in TEMPLE_DATA.items():   ALL_DATA[k] = {**v, "category":"temple"}

# ── Helpers ───────────────────────────────────────────────────
def img_path(name):
    for ext in ["jpg","jpeg","png","webp","JPG","JPEG","PNG"]:
        p = os.path.join(IMG_DIR, f"{name}.{ext}")
        if os.path.exists(p): return p
    return None

def run_yolo_people_only(path_or_img, conf=0.15, annotate=False):
    """Detect ONLY people (class 0). All other objects ignored."""
    if isinstance(path_or_img, str):
        img = cv2.imread(path_or_img)
    else:
        img = path_or_img
    if img is None: return 0, None
    h, w = img.shape[:2]
    if max(h,w) > 1280:
        scale = 1280/max(h,w)
        img = cv2.resize(img,(int(w*scale),int(h*scale)))
    results = model(img, conf=conf, classes=[0], verbose=False)  # classes=[0] = people only
    count   = sum(len(r.boxes) for r in results)
    ann_b64 = None
    if annotate:
        annotated = results[0].plot()
        _, buf = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 82])
        ann_b64 = "data:image/jpeg;base64," + base64.b64encode(buf).decode()
    return count, ann_b64

def get_next_arrival(schedule):
    """Calculate next bus arrival from schedule."""
    now = datetime.now()
    current = now.hour * 60 + now.minute
    for t in schedule:
        h, m = map(int, t.split(":"))
        total = h * 60 + m
        diff  = total - current
        if diff > 0:
            if diff < 60: return f"{diff} mins"
            else:         return f"{diff//60}h {diff%60}m"
    return "Last bus departed"

def bus_status(count):
    if count > 45: return "High"
    elif count >= 20: return "Medium"
    else: return "Low"

def hospital_status(count):
    if count > 30: return "High"
    elif count >= 10: return "Medium"
    else: return "Low"

def temple_status(count):
    if count > 40: return "High"
    elif count >= 15: return "Medium"
    else: return "Low"

def queue_risk(count):
    if count > 20:   return "High",   "High",   "Critical"
    elif count >= 10: return "Medium", "Medium", "Crowded"
    elif count >= 5:  return "Medium", "Medium", "Moderate"
    else:             return "Low",    "Low",    "Safe"

def encode_image(path):
    try:
        with open(path,"rb") as f: data = base64.b64encode(f.read()).decode()
        ext  = path.rsplit(".",1)[-1].lower()
        mime = "image/jpeg" if ext in ("jpg","jpeg") else f"image/{ext}"
        return f"data:{mime};base64,{data}"
    except: return ""

def simulate_count(base, category):
    """Add realistic random fluctuation for demo."""
    hour = datetime.now().hour
    if category == "bus":
        peak = 1.5 if (7 <= hour <= 10 or 17 <= hour <= 20) else 0.8
    elif category == "hospital":
        peak = 1.3 if (9 <= hour <= 14) else 0.7
    else:  # temple
        peak = 1.4 if (6 <= hour <= 9 or 17 <= hour <= 19) else 0.6
    simulated = int(base * peak + random.randint(-5, 8))
    return max(0, simulated)

# ── Auth ──────────────────────────────────────────────────────
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated

# ── Routes ────────────────────────────────────────────────────
@app.route("/")
def root():
    if session.get("user"): return redirect(url_for("home"))
    return redirect(url_for("login_page"))

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/api/login", methods=["POST"])
def api_login():
    data     = request.get_json()
    email    = data.get("email","").strip().lower()
    password = data.get("password","").strip()
    if email in USERS and USERS[email] == password:
        session["user"]  = email
        session["name"]  = email.split("@")[0].title()
        return jsonify({"success": True, "name": session["name"]})
    return jsonify({"success": False, "error": "Invalid email or password"}), 401

@app.route("/api/logout")
def api_logout():
    session.clear()
    return redirect(url_for("login_page"))

@app.route("/home")
@login_required
def home(): return render_template("index.html", user=session.get("name","User"))

@app.route("/bus")
@login_required
def bus(): return render_template("bus.html")

@app.route("/hospital")
@login_required
def hospital(): return render_template("hospital.html")

@app.route("/temple")
@login_required
def temple(): return render_template("temple.html")

@app.route("/queue")
@login_required
def queue(): return render_template("queue.html")

@app.route("/dashboard")
@login_required
def dashboard(): return render_template("dashboard.html")

# ── Bus API ───────────────────────────────────────────────────
@app.route("/api/bus")
def api_bus():
    q = request.args.get("q","").lower().strip().replace(" ","")
    if q not in BUS_DATA:
        matches = [{"key":k,"label":v["label"],"route":v["route"]}
                   for k,v in BUS_DATA.items() if q in k or q in v["label"].lower()]
        return jsonify({"error":f"Bus '{q.upper()}' not found","suggestions":matches[:5]}), 404
    meta  = BUS_DATA[q]
    path  = img_path(q)
    count, ann = run_yolo_people_only(path, conf=0.15, annotate=True) if path else (0,None)
    count = simulate_count(count if path else random.randint(5,60), "bus")
    return jsonify({
        "key": q, "label": meta["label"], "route": meta["route"],
        "destination": meta["destination"], "capacity": meta["capacity"],
        "next_arrival": get_next_arrival(meta["schedule"]),
        "best_time": "Peak: 7-10AM & 5-8PM",
        "count": count, "status": bus_status(count),
        "wait": count * 2,
        "pct": min(int(count/meta["capacity"]*100),100),
        "image": encode_image(path) if path else "",
        "annotated": ann or "",
    })

@app.route("/api/buses/search")
def api_buses_search():
    q = request.args.get("q","").lower().strip()
    results = []
    for k,v in BUS_DATA.items():
        if (q in k or q in v["label"].lower() or
            q in v["route"].lower() or q in v["destination"].lower()):
            results.append({"key":k,"label":v["label"],"route":v["route"],
                            "destination":v["destination"],"capacity":v["capacity"],
                            "next_arrival":get_next_arrival(v["schedule"])})
    return jsonify(results[:20])

@app.route("/api/buses/all")
def api_buses_all():
    return jsonify([{"key":k,"label":v["label"],"route":v["route"],
                     "destination":v["destination"]} for k,v in BUS_DATA.items()])

# ── Hospital API ──────────────────────────────────────────────
@app.route("/api/hospitals")
def api_hospitals():
    results = []
    for k,v in HOSPITAL_DATA.items():
        path  = img_path(k)
        count,_ = run_yolo_people_only(path,conf=0.15) if path else (0,None)
        count = simulate_count(count if path else random.randint(3,40),"hospital")
        results.append({"key":k,"label":v["label"],"location":v["location"],
                        "type":v["type"],"best_time":v["best_time"],
                        "capacity":v["capacity"],"count":count,
                        "status":hospital_status(count),"wait":count*2,
                        "image":encode_image(path) if path else ""})
    return jsonify(results)

@app.route("/api/hospital")
def api_hospital():
    q = request.args.get("q","").lower().strip()
    if q not in HOSPITAL_DATA:
        return jsonify({"error": f"Hospital '{q}' not found"}), 404
    meta  = HOSPITAL_DATA[q]
    path  = img_path(q)
    count, ann = run_yolo_people_only(path, conf=0.15, annotate=True) if path else (0,None)
    count = simulate_count(count if path else random.randint(3,40), "hospital")
    density = "High" if count > 30 else "Medium" if count >= 10 else "Low"
    risk = "Critical" if count > 40 else "Crowded" if count > 20 else "Moderate" if count >= 5 else "Safe"
    return jsonify({
        "key": q, "label": meta["label"], "location": meta["location"],
        "type": meta["type"], "capacity": meta["capacity"],
        "best_time": meta["best_time"],
        "count": count, "status": hospital_status(count), "density": density, "risk": risk,
        "wait": count * 2,
        "image": encode_image(path) if path else "",
        "annotated": ann or "",
        "simulated": path is None,
    })

# ── Temple API ────────────────────────────────────────────────
@app.route("/api/temples")
def api_temples():
    results = []
    for k,v in TEMPLE_DATA.items():
        path  = img_path(k)
        count,_ = run_yolo_people_only(path,conf=0.15) if path else (0,None)
        count = simulate_count(count if path else random.randint(5,80),"temple")
        results.append({"key":k,"label":v["label"],"location":v["location"],
                        "deity":v["deity"],"best_time":v["best_time"],
                        "capacity":v["capacity"],"count":count,
                        "status":temple_status(count),"wait":count*2,
                        "image":encode_image(path) if path else ""})
    return jsonify(results)

@app.route("/api/temple")
def api_temple():
    q = request.args.get("q","").lower().strip()
    if q not in TEMPLE_DATA:
        return jsonify({"error": f"Temple '{q}' not found"}), 404
    meta  = TEMPLE_DATA[q]
    path  = img_path(q)
    count, ann = run_yolo_people_only(path, conf=0.15, annotate=True) if path else (0,None)
    count = simulate_count(count if path else random.randint(5,80), "temple")
    density = "High" if count > 40 else "Medium" if count >= 15 else "Low"
    risk = "Critical" if count > 50 else "Crowded" if count > 25 else "Moderate" if count >= 5 else "Safe"
    return jsonify({
        "key": q, "label": meta["label"], "location": meta["location"],
        "deity": meta["deity"], "capacity": meta["capacity"],
        "best_time": meta["best_time"],
        "count": count, "status": temple_status(count), "density": density, "risk": risk,
        "wait": count * 2,
        "image": encode_image(path) if path else "",
        "annotated": ann or "",
        "simulated": path is None,
    })

# ── Upload API ────────────────────────────────────────────────
@app.route("/api/upload", methods=["POST"])
def api_upload():
    if "image" not in request.files:
        return jsonify({"error":"No image"}),400
    file  = request.files["image"]
    npimg = np.frombuffer(file.read(),np.uint8)
    img   = cv2.imdecode(npimg,cv2.IMREAD_COLOR)
    if img is None: return jsonify({"error":"Bad image"}),400
    count, ann = run_yolo_people_only(img,conf=0.15,annotate=True)
    crowd,density,risk = queue_risk(count)
    return jsonify({"people":count,"status":crowd,"density":density,
                    "risk":risk,"waiting_time":count*2,"annotated":ann})

# ── Video frame API ───────────────────────────────────────────
@app.route("/api/video_frame", methods=["POST"])
def api_video_frame():
    """Process a single video frame — people only YOLO."""
    data = request.get_json()
    if not data or "frame" not in data:
        return jsonify({"error":"No frame"}),400
    try:
        b64   = data["frame"].split(",")[-1]
        npimg = np.frombuffer(base64.b64decode(b64),np.uint8)
        img   = cv2.imdecode(npimg,cv2.IMREAD_COLOR)
    except: return jsonify({"error":"Decode failed"}),400
    if img is None: return jsonify({"error":"Bad frame"}),400
    count, ann = run_yolo_people_only(img,conf=0.15,annotate=True)
    crowd,density,risk = queue_risk(count)
    return jsonify({"people":count,"status":crowd,"density":density,
                    "risk":risk,"waiting_time":count*2,"annotated":ann})

# ── Capture (webcam) API ──────────────────────────────────────
@app.route("/api/capture", methods=["POST"])
def api_capture():
    data = request.get_json()
    if not data or "frame" not in data:
        return jsonify({"error":"No frame"}),400
    try:
        b64   = data["frame"].split(",")[-1]
        npimg = np.frombuffer(base64.b64decode(b64),np.uint8)
        img   = cv2.imdecode(npimg,cv2.IMREAD_COLOR)
    except: return jsonify({"error":"Decode failed"}),400
    if img is None: return jsonify({"error":"Bad frame"}),400
    count, ann = run_yolo_people_only(img,conf=0.15,annotate=True)
    crowd,density,risk = queue_risk(count)
    return jsonify({"people":count,"status":crowd,"density":density,
                    "risk":risk,"waiting_time":count*2,"annotated":ann})

# ── Summary API ───────────────────────────────────────────────
@app.route("/api/summary")
def api_summary():
    results = []
    for k,v in BUS_DATA.items():
        count = simulate_count(random.randint(5,60),"bus")
        results.append({"key":k,"label":v["label"],"category":"Bus",
                        "count":count,"status":bus_status(count),
                        "capacity":v["capacity"],"location":v["destination"]})
    for k,v in HOSPITAL_DATA.items():
        path  = img_path(k)
        count,_ = run_yolo_people_only(path) if path else (0,None)
        count = simulate_count(count if path else random.randint(3,40),"hospital")
        results.append({"key":k,"label":v["label"],"category":"Hospital",
                        "count":count,"status":hospital_status(count),
                        "capacity":v["capacity"],"location":v["location"]})
    for k,v in TEMPLE_DATA.items():
        path  = img_path(k)
        count,_ = run_yolo_people_only(path) if path else (0,None)
        count = simulate_count(count if path else random.randint(5,80),"temple")
        results.append({"key":k,"label":v["label"],"category":"Temple",
                        "count":count,"status":temple_status(count),
                        "capacity":v["capacity"],"location":v["location"]})
    total  = sum(r["count"] for r in results)
    busiest = max(results,key=lambda x:x["count"],default={"label":"N/A","count":0})
    return jsonify({"locations":results,"total_people":total,
                    "high_count":sum(1 for r in results if r["status"]=="High"),
                    "medium_count":sum(1 for r in results if r["status"]=="Medium"),
                    "low_count":sum(1 for r in results if r["status"]=="Low"),
                    "busiest":busiest,"avg_wait":round(total*2/len(results)) if results else 0,
                    "total_locations":len(results),
                    "timestamp":datetime.now().strftime("%H:%M:%S")})

# ── Suggest API ───────────────────────────────────────────────
@app.route("/api/suggest")
def api_suggest():
    q = request.args.get("q","").lower().strip()
    matches = [k for k in ALL_DATA if k.startswith(q) or q in k or
               q in ALL_DATA[k].get("label","").lower()]
    return jsonify([{"key":k,"label":ALL_DATA[k]["label"],
                     "category":ALL_DATA[k]["category"]} for k in matches[:10]])

@app.route("/api/debug")
def api_debug():
    return jsonify({k:{"found":img_path(k) is not None,
                       "path":img_path(k) or "NOT FOUND"} for k in ALL_DATA})

if __name__ == "__main__":
    print(f"\n{'='*55}\n  CrowdSenseAI — Starting\n{'='*55}")
    print(f"  Images folder : {IMG_DIR}")
    print(f"  Folder exists : {os.path.exists(IMG_DIR)}")
    print(f"  Open: http://127.0.0.1:5000\n{'='*55}\n")
    app.run(debug=True, host="0.0.0.0", port=5000)