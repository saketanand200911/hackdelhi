"""
PlantVillage Master Agronomy Pathology Engine
Contains complete ground-truth disease definitions, leaf morphology,
lesion patterns, organic and chemical treatments, and local outbreak protocols
for all PlantVillage classes PLUS extended global & Indian agricultural crops:
Apple, Blueberry, Cherry, Corn (Maize), Grape, Orange/Citrus, Peach, Pepper/Chilli,
Potato, Raspberry, Soybean, Squash/Cucurbits, Strawberry, Tomato, Coffee, Rice (Paddy),
Wheat, Cotton, Banana, Mango, Sugarcane, Tea, Groundnut (Peanut), Mustard, and Onion.
"""

from typing import Dict, Any, List, Optional
import re

PLANTVILLAGE_MASTER_DB: Dict[str, Dict[str, Any]] = {
    # ==================== APPLE ====================
    "Apple___Apple_scab": {
        "crop": "Apple",
        "disease": "Apple Scab (Venturia inaequalis)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Simple ovate leaves with finely serrated margins",
        "color_signature": "Olive-green to dark velvety brown/black lesions",
        "lesion_pattern": "Dull circular velvety spots that pucker and curl the leaf lamina",
        "is_healthy": False,
        "severity": "Moderate to High",
        "organic_treatment": [
            "Apply liquid copper soap or wettable sulfur before bloom",
            "Rake, chop, and compost fallen autumn leaves to eliminate overwintering ascocarps",
            "Prune inner canopy branches to maximize air movement and fast drying"
        ],
        "chemical_treatment": [
            "Spray Mancozeb 75% WP @ 2.0g/L or Captan 50% WP @ 2.5g/L during primary infection",
            "Apply Difenoconazole 25% EC at pink bud stage if infection pressure is severe"
        ],
        "outbreak_risk": "High (rain and high humidity trigger ascospore release across orchard)",
        "neighbor_alert": "Scab ascospores are actively discharging during rainfall. Neighboring orchards within 1.5km should apply protective fungicide before next rain.",
        "hindi_summary": "सेब की पत्ती में स्कैब रोग के लक्षण (काले-जैतूनी धब्बे) हैं। कॉपर या मैनकोजेब का छिड़काव करें और नीचे गिरी सूखी पत्तियां जला दें।"
    },
    "Apple___Black_rot": {
        "crop": "Apple",
        "disease": "Black Rot / Frogeye Leaf Spot (Botryosphaeria obtusa)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Simple ovate leaves with serrated margins",
        "color_signature": "Purple specks enlarging to tan/light brown centers with dark purple rings",
        "lesion_pattern": "'Frogeye' spots with circular light centers and double concentric margins",
        "is_healthy": False,
        "severity": "Moderate",
        "organic_treatment": [
            "Prune out dead shoots, mummified fruits, and cankers during dormant winter pruning",
            "Apply Bordeaux mixture (4:4:50) at bud break"
        ],
        "chemical_treatment": [
            "Apply Thiophanate-methyl 70% WP @ 1.0g/L or Captan 50% WP @ 2.0g/L",
            "Spray Trifloxystrobin + Tebuconazole @ 0.5g/L at petal fall"
        ],
        "outbreak_risk": "Moderate",
        "neighbor_alert": "Black rot canker inoculum detected. Prune infected wood and dispose away from borders.",
        "hindi_summary": "सेब की पत्ती में ब्लैक रॉट (मेंढक की आंख जैसे धब्बे) हैं। सूखी टहनियां काटें और कैप्टान का छिड़काव करें।"
    },
    "Apple___Cedar_apple_rust": {
        "crop": "Apple",
        "disease": "Cedar Apple Rust (Gymnosporangium juniperi-virginianae)",
        "pathogen_type": "Fungal (Heteroecious)",
        "leaf_morphology": "Simple ovate leaves with serrated margins",
        "color_signature": "Brilliant bright orange-yellow circular spots",
        "lesion_pattern": "Bright yellow-orange spots on upper surface; small tubular aecia cups beneath",
        "is_healthy": False,
        "severity": "Moderate",
        "organic_treatment": [
            "Remove Eastern red cedar / juniper trees within 1-2 km radius",
            "Apply sulfur or copper octanoate spray early in spring as cedar galls open"
        ],
        "chemical_treatment": [
            "Spray Myclobutanil 10% WP @ 0.4g/L or Mancozeb 75% WP @ 2.0g/L at pink bud to petal fall"
        ],
        "outbreak_risk": "Moderate (depends on proximity to juniper alternate hosts)",
        "neighbor_alert": "Cedar rust galls are gelatinizing on nearby junipers. Apply protective spray immediately.",
        "hindi_summary": "सेब की पत्ती पर नारंगी-पीले जंग के धब्बे हैं। जुनिपर के पेड़ों को दूर रखें और माइक्लोबुटानिल का छिड़काव करें।"
    },
    "Apple___healthy": {
        "crop": "Apple",
        "disease": "Healthy Apple Foliage",
        "pathogen_type": "None",
        "leaf_morphology": "Simple ovate leaves with fine serrations",
        "color_signature": "Uniform deep green glossy surface",
        "lesion_pattern": "Unblemished green lamina, clear venation, no lesions or cupping",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Maintain routine organic neem oil spray and balanced orchard compost."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Foliage in clean healthy condition.",
        "hindi_summary": "सेब की पत्तियां पूरी तरह स्वस्थ और हरी हैं। कोई कीटनाशक की आवश्यकता नहीं है।"
    },

    # ==================== BLUEBERRY ====================
    "Blueberry___healthy": {
        "crop": "Blueberry",
        "disease": "Healthy Blueberry Foliage",
        "pathogen_type": "None",
        "leaf_morphology": "Small elliptical smooth-margined glossy leaves",
        "color_signature": "Deep glossy green lamina",
        "lesion_pattern": "Healthy smooth leaf surface without rust, spots, or chlorosis",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Maintain acidic soil pH (4.5 - 5.2) with pine bark mulch and elemental sulfur."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Blueberry bushes are vigorous and healthy.",
        "hindi_summary": "ब्लूबेरी की पत्तियां स्वस्थ हैं। मिट्टी का पीएच अम्लीय बनाए रखें।"
    },

    # ==================== CHERRY ====================
    "Cherry___Powdery_mildew": {
        "crop": "Cherry",
        "disease": "Powdery Mildew (Podosphaera clandestina)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Ovate to obovate serrated leaves",
        "color_signature": "White circular powdery felt patches on leaf surface",
        "lesion_pattern": "Patches of white talcum-like mycelial growth causing upward leaf curling and distortion",
        "is_healthy": False,
        "severity": "Moderate",
        "organic_treatment": [
            "Spray potassium bicarbonate (3g/L) or neem oil emulsion (5ml/L)",
            "Improve sun penetration and air circulation through proper pruning"
        ],
        "chemical_treatment": [
            "Apply Myclobutanil 10% WP @ 0.5g/L or Hexaconazole 5% EC @ 1ml/L"
        ],
        "outbreak_risk": "High in shaded, warm, humid conditions",
        "neighbor_alert": "Powdery mildew conidia spreading on wind currents. Check tender terminal shoot tips.",
        "hindi_summary": "चेरी की पत्ती पर सफेद चूर्ण (पाउडरी मिल्ड्यू) जमा है। पोटेशियम बाइकार्बोनेट या हेक्साकोनाजोल का छिड़काव करें।"
    },
    "Cherry___healthy": {
        "crop": "Cherry",
        "disease": "Healthy Cherry Foliage",
        "pathogen_type": "None",
        "leaf_morphology": "Ovate leaves with serrated margins and glands on petiole",
        "color_signature": "Vibrant emerald green",
        "lesion_pattern": "Intact leaf blades free of shot-holes, powdery mold, or necrotic spots",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Regular orchard care and organic compost tea."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Cherry foliage is clear and robust.",
        "hindi_summary": "चेरी की पत्तियां स्वस्थ हैं।"
    },

    # ==================== CORN (MAIZE) ====================
    "Corn___Cercospora_leaf_spot_Gray_leaf_spot": {
        "crop": "Corn (Maize)",
        "disease": "Gray Leaf Spot (Cercospora zeae-maydis)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Long linear strap-like monocot blades with parallel veins",
        "color_signature": "Tan to grayish rectangular lesions delimited strictly by leaf veins",
        "lesion_pattern": "Strictly rectangular block lesions running parallel to leaf veins; turn gray with spores",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Rotate crops for at least 2 years away from maize",
            "Chop and till corn residue deep into soil to accelerate microbial breakdown"
        ],
        "chemical_treatment": [
            "Apply Azoxystrobin + Difenoconazole @ 1ml/L at tasseling (VT/R1 stage)",
            "Spray Pyraclostrobin 20% WG @ 1g/L on lower canopy if lesions appear early"
        ],
        "outbreak_risk": "High (wind and rain splash carry spores across neighboring fields)",
        "neighbor_alert": "Gray Leaf Spot spreading on corn. If lesions reach the ear leaf before blister stage, spray immediately.",
        "hindi_summary": "मक्के की पत्ती में नसों के बीच लंबे चौकोर भूरे धब्बे (ग्रे लीफ स्पॉट) हैं। एजॉक्सीस्ट्रोबिन का छिड़काव करें।"
    },
    "Corn___Common_rust": {
        "crop": "Corn (Maize)",
        "disease": "Common Rust (Puccinia sorghi)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Long linear monocot blades with parallel veins",
        "color_signature": "Golden brown to cinnamon-brown powdery pustules",
        "lesion_pattern": "Small circular to elongate cinnamon-brown uredinial pustules scattered on both leaf surfaces",
        "is_healthy": False,
        "severity": "Moderate to High",
        "organic_treatment": [
            "Plant resistant hybrid cultivars",
            "Early morning planting to avoid peak airborne urediniospore waves"
        ],
        "chemical_treatment": [
            "Spray Mancozeb 75% WP @ 2.5g/L or Tebuconazole 25.9% EC @ 1ml/L at first sign of pustules"
        ],
        "outbreak_risk": "High (airborne spores travel hundreds of kilometers on southern winds)",
        "neighbor_alert": "Corn rust pustules actively rupturing. Neighboring farms should inspect leaves above ear level.",
        "hindi_summary": "मक्के की पत्तियों पर भूरे-नारंगी जंग के फफोले हैं। मैनकोजेब या टेबुकोनाजोल का छिड़काव करें।"
    },
    "Corn___Northern_Leaf_Blight": {
        "crop": "Corn (Maize)",
        "disease": "Northern Corn Leaf Blight (Exserohilum turcicum)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Long linear monocot blades with parallel veins",
        "color_signature": "Long grayish-green to tan cigar-shaped elliptical lesions",
        "lesion_pattern": "Large (2.5 - 15 cm) cigar-shaped or elliptical lesions with rounded ends",
        "is_healthy": False,
        "severity": "High to Critical",
        "organic_treatment": [
            "Plow under corn stalks immediately after harvest",
            "Plant NCLB resistant hybrid seeds with Ht gene"
        ],
        "chemical_treatment": [
            "Spray Propiconazole 25% EC @ 1ml/L or Azoxystrobin 23% SC @ 1ml/L"
        ],
        "outbreak_risk": "High in cool (18-27°C), wet, dewy conditions",
        "neighbor_alert": "Northern Leaf Blight detected. Spreading along prevailing wind corridor.",
        "hindi_summary": "मक्के की पत्ती पर सिगार के आकार के बड़े भूरे-धूसर घाव हैं। प्रोपिकोनाजोल का छिड़काव करें।"
    },
    "Corn___healthy": {
        "crop": "Corn (Maize)",
        "disease": "Healthy Corn Foliage",
        "pathogen_type": "None",
        "leaf_morphology": "Long arching linear blades with parallel veins and intact midrib",
        "color_signature": "Deep vibrant green",
        "lesion_pattern": "Smooth green surface without pustules, stripes, or necrotic blight",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Maintain balanced nitrogen sidedressing and weed-free spacing."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Corn crop is vigorous and healthy.",
        "hindi_summary": "मक्के का पौधा पूरी तरह स्वस्थ और हरा है।"
    },

    # ==================== GRAPE ====================
    "Grape___Black_rot": {
        "crop": "Grape",
        "disease": "Grape Black Rot (Guignardia bidwellii)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Palmately 3-5 lobed leaves with cordate base and toothed margins",
        "color_signature": "Small reddish-brown circular spots with dark brown margins",
        "lesion_pattern": "Circular necrotic spots with tiny black pycnidia specks arranged in rings inside lesion",
        "is_healthy": False,
        "severity": "Severe",
        "organic_treatment": [
            "Prune canopy aggressively for sunlight and fast canopy drying",
            "Remove all dried mummified grape clusters from vines and ground"
        ],
        "chemical_treatment": [
            "Spray Mancozeb 75% WP @ 2g/L or Kresoxim-methyl 44.3% SC @ 0.7ml/L before bloom"
        ],
        "outbreak_risk": "High (spores splash from overwintered mummies during warm spring rain)",
        "neighbor_alert": "Black rot inoculum active in vineyard. Spray protective fungicides before rain event.",
        "hindi_summary": "अंगूर की पत्ती पर काले छल्ले वाले लाल-भूरे धब्बे हैं। मैनकोजेब का छिड़काव करें और सूखे अंगूर हटाएं।"
    },
    "Grape___Esca_Black_Measles": {
        "crop": "Grape",
        "disease": "Esca / Black Measles (Complex: Phaeomoniella / Phaeoacremonium)",
        "pathogen_type": "Fungal Wood Decay Complex",
        "leaf_morphology": "Palmately lobed leaves",
        "color_signature": "Interveinal yellow and red discoloration with green veins ('Tiger-stripe')",
        "lesion_pattern": "Dramatic 'tiger-stripe' necrosis between major veins while primary veins stay green",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Paint all large pruning cuts immediately with biological paste (Trichoderma)",
            "Mark symptomatic vines and prune last to prevent shears from carrying fungus"
        ],
        "chemical_treatment": [
            "No chemical cure exists for internal trunk decay; apply wound sealants after pruning"
        ],
        "outbreak_risk": "Moderate (slow trunk spread through pruning tool contamination)",
        "neighbor_alert": "Esca trunk disease identified. Sterilize shears with 70% alcohol between vines.",
        "hindi_summary": "अंगूर में एस्का (बाघ की धारियों जैसे पत्ते) रोग है। छंटाई के औजारों को सैनिटाइज करें और घावों पर पेस्ट लगाएं।"
    },
    "Grape___Leaf_blight_Isariopsis_Leaf_Spot": {
        "crop": "Grape",
        "disease": "Grape Leaf Blight (Pseudocercospora vitis / Isariopsis)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Palmately lobed grape leaves",
        "color_signature": "Irregular dark brown to black angular lesions with yellow halo",
        "lesion_pattern": "Lesions are sharply delimited by leaf veinlets, giving an angular shape; leaf drops early",
        "is_healthy": False,
        "severity": "Moderate",
        "organic_treatment": [
            "Spray copper oxychloride (3g/L) after harvest to protect foliage",
            "Rake and bury infected fallen leaves"
        ],
        "chemical_treatment": [
            "Apply Carbendazim 50% WP @ 1g/L or Azoxystrobin @ 1ml/L"
        ],
        "outbreak_risk": "Moderate",
        "neighbor_alert": "Leaf blight causing premature defoliation in grape vines.",
        "hindi_summary": "अंगूर की पत्ती पर अनियमित गहरे भूरे धब्बे हैं। कॉपर ऑक्सीक्लोराइड या कार्बेन्डाजिम का छिड़काव करें।"
    },
    "Grape___healthy": {
        "crop": "Grape",
        "disease": "Healthy Grape Foliage",
        "pathogen_type": "None",
        "leaf_morphology": "Broad palmately lobed green leaves",
        "color_signature": "Lush emerald green",
        "lesion_pattern": "Uniform green canopy without tiger stripes, black spots, or mold",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Maintain canopy shoot thinning and good trellis airflow."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Vineyard foliage is clean and healthy.",
        "hindi_summary": "अंगूर की पत्तियां स्वस्थ और हरी हैं।"
    },

    # ==================== ORANGE & CITRUS ====================
    "Orange___Haunglongbing_Citrus_greening": {
        "crop": "Orange / Citrus",
        "disease": "Citrus Greening / Huanglongbing (Candidatus Liberibacter asiaticus)",
        "pathogen_type": "Bacterial (Vector: Asian Citrus Psyllid)",
        "leaf_morphology": "Unifoliolate ovate leaves with winged petioles",
        "color_signature": "Asymmetrical blotchy yellow mottle across the leaf lamina",
        "lesion_pattern": "Blotchy mottle (yellow pattern does not mirror across midrib), yellow veins, upright leaves",
        "is_healthy": False,
        "severity": "Critical",
        "organic_treatment": [
            "Release parasitoid wasps (Tamarixia radiata) to biological control psyllid vector",
            "Spray horticultural petroleum mineral oil (1-2%) to deter psyllids",
            "Eradicate and burn severely infected symptomatic trees"
        ],
        "chemical_treatment": [
            "Control psyllid vector with Imidacloprid 17.8% SL @ 0.5ml/L or Thiamethoxam 25% WG @ 0.3g/L",
            "Foliar micronutrient nutritional sprays (Zinc, Iron, Manganese) to support tree vigor"
        ],
        "outbreak_risk": "Critical (quarantine pest; psyllids spread bacteria across entire regions)",
        "neighbor_alert": "CITRUS GREENING VECTOR ALERT: Asian Citrus Psyllid detected. Neighboring citrus orchards within 5km must spray psyllid insecticide.",
        "hindi_summary": "नींबू/संतरे में सिट्रस ग्रीनिंग (पत्तियों का बेढंगा पीलापन) है। साइला कीड़े को मारने के लिए इमिडाक्लोप्रिड का छिड़काव करें।"
    },
    "Citrus___Citrus_canker": {
        "crop": "Orange / Citrus",
        "disease": "Citrus Canker (Xanthomonas citri)",
        "pathogen_type": "Bacterial",
        "leaf_morphology": "Elliptical dark green leaves with winged petiole",
        "color_signature": "Raised corky tan/brown crater pustules with yellow chlorotic halo",
        "lesion_pattern": "Raised blister-like eruptions on both sides of leaf surrounded by distinctive oily water-soaked yellow halo",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Spray copper hydroxide (2.5g/L) during flush emergence",
            "Prune infected twigs during dry season"
        ],
        "chemical_treatment": [
            "Copper Oxychloride 50% WP @ 3g/L + Streptocycline (antibacterial) @ 100ppm"
        ],
        "outbreak_risk": "High (wind-driven rain spreads bacteria rapidly)",
        "neighbor_alert": "Citrus canker bacteria spreading via rain splash. Protect young leaf flush.",
        "hindi_summary": "नींबू में कैंकर रोग (उभरे हुए खुरदुरे धब्बे और पीला घेरा) है। कॉपर ऑक्सीक्लोराइड और स्ट्रेप्टोसाइक्लिन का छिड़काव करें।"
    },

    # ==================== PEACH ====================
    "Peach___Bacterial_spot": {
        "crop": "Peach",
        "disease": "Peach Bacterial Spot (Xanthomonas arboricola pv. pruni)",
        "pathogen_type": "Bacterial",
        "leaf_morphology": "Lanceolate slender leaves with finely serrated margins",
        "color_signature": "Small angular dark purple to black water-soaked lesions",
        "lesion_pattern": "Center of lesions dries, cracks, and falls out, creating a distinct 'shot-hole' appearance",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Apply fixed copper sprays at dormant bud swell before leaves emerge",
            "Avoid excessive nitrogen fertilization which produces soft vulnerable tissue"
        ],
        "chemical_treatment": [
            "Spray Oxytetracycline @ 150ppm or Copper hydroxide at low rates during growing season"
        ],
        "outbreak_risk": "High (wind-driven rain spreads bacteria rapidly)",
        "neighbor_alert": "Bacterial shot-hole active in peach orchard. Avoid overhead sprinkler irrigation.",
        "hindi_summary": "आड़ू की पत्ती पर छेद (शॉट-होल) और बैंगनी धब्बे हैं। कॉपर हाइड्रोक्साइड का छिड़काव करें।"
    },
    "Peach___healthy": {
        "crop": "Peach",
        "disease": "Healthy Peach Foliage",
        "pathogen_type": "None",
        "leaf_morphology": "Long lanceolate leaves with fine serrations",
        "color_signature": "Smooth glossy vibrant green",
        "lesion_pattern": "Flawless green lamina without shot-holes, leaf curl, or bacterial specks",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Routine orchard sanitation and organic mulch."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Peach trees are clean and thriving.",
        "hindi_summary": "आड़ू की पत्तियां पूरी तरह स्वस्थ हैं।"
    },

    # ==================== PEPPER & CHILLI ====================
    "Pepper__bell___Bacterial_spot": {
        "crop": "Pepper (Bell / Chilli)",
        "disease": "Bacterial Spot (Xanthomonas euvesicatoria)",
        "pathogen_type": "Bacterial",
        "leaf_morphology": "Simple ovate leaves with smooth edges and acute apex",
        "color_signature": "Small circular to irregular dark brown water-soaked lesions with yellow halo",
        "lesion_pattern": "Lesions on lower leaf surface appear blistered; leaves turn yellow and drop prematurely",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Treat seeds with hot water (50°C for 25 minutes) before sowing",
            "Apply copper sulfate pentahydrate or Bacillus subtilis formulations"
        ],
        "chemical_treatment": [
            "Spray Copper Oxychloride 50% WP @ 2.5g/L + Streptomycin sulfate @ 100ppm every 7-10 days"
        ],
        "outbreak_risk": "High in warm (24-30°C) rainy periods with wind",
        "neighbor_alert": "Bacterial spot outbreak on pepper/chilli plots. Avoid handling plants when wet.",
        "hindi_summary": "मिर्च की पत्ती पर काले-भूरे जलयुक्त धब्बे हैं। कॉपर और स्ट्रेप्टोसाइक्लिन का छिड़काव करें।"
    },
    "Pepper__bell___healthy": {
        "crop": "Pepper (Bell / Chilli)",
        "disease": "Healthy Pepper Foliage",
        "pathogen_type": "None",
        "leaf_morphology": "Simple ovate to elliptical leaves with smooth margins",
        "color_signature": "Uniform glossy dark green",
        "lesion_pattern": "Smooth, flat, unblemished leaves with no chlorosis, leaf curl, or spots",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Maintain balanced fertigation and regular weeding."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Chilli/Pepper plants are vigorous and disease-free.",
        "hindi_summary": "मिर्च के पौधे स्वस्थ और हरे-भरे हैं।"
    },
    "Pepper__bell___Anthracnose": {
        "crop": "Pepper (Bell / Chilli)",
        "disease": "Chilli Anthracnose / Dieback (Colletotrichum capsici)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Simple ovate leaves",
        "color_signature": "Circular sunken spots with concentric rings of black acervuli specks",
        "lesion_pattern": "Necrotic patches on leaves; twigs die back from top downwards",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Seed treatment with Trichoderma viride @ 10g/kg",
            "Remove and destroy affected twigs and fruits"
        ],
        "chemical_treatment": [
            "Spray Azoxystrobin 23% SC @ 1ml/L or Difenoconazole 25% EC @ 1ml/L"
        ],
        "outbreak_risk": "High during humid monsoons",
        "neighbor_alert": "Anthracnose dieback active on chilli. Spray protective triazole fungicide.",
        "hindi_summary": "मिर्च में एन्थ्रेक्नोज (डाई-बैक) रोग है। एजॉक्सीस्ट्रोबिन या डाइफेनोकोनाजोल का छिड़काव करें।"
    },

    # ==================== POTATO ====================
    "Potato___Early_blight": {
        "crop": "Potato",
        "disease": "Potato Early Blight (Alternaria solani)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Pinnately compound leaves with oval leaflets",
        "color_signature": "Dark brown circular spots with concentric target rings (bullseye)",
        "lesion_pattern": "Concentric rings surrounded by narrow chlorotic yellow halos, starting on oldest bottom leaves",
        "is_healthy": False,
        "severity": "Moderate to High",
        "organic_treatment": [
            "Mulch heavily with clean straw to prevent soil-borne spores splashing onto lower leaves",
            "Maintain 3-year crop rotation with non-solanaceous crops"
        ],
        "chemical_treatment": [
            "Spray Chlorothalonil 75% WP @ 2g/L or Mancozeb 75% WP @ 2.5g/L",
            "Apply Azoxystrobin + Difenoconazole @ 1ml/L at early onset"
        ],
        "outbreak_risk": "Moderate to High in alternating wet and dry weather",
        "neighbor_alert": "Early blight target spots multiplying on lower canopy. Apply preventive fungicide spray.",
        "hindi_summary": "आलू के निचले पत्तों पर छल्लेदार (बुलआई) भूरे धब्बे हैं। मैनकोजेब या क्लोरोथैलोनिल का छिड़काव करें।"
    },
    "Potato___Late_blight": {
        "crop": "Potato",
        "disease": "Potato Late Blight (Phytophthora infestans)",
        "pathogen_type": "Oomycete",
        "leaf_morphology": "Pinnately compound potato foliage",
        "color_signature": "Water-soaked dark green-black greasy lesions with pale chlorotic border",
        "lesion_pattern": "Rapidly enlarging dark water-soaked patches; white cottony fungal growth on underside in high humidity",
        "is_healthy": False,
        "severity": "Critical",
        "organic_treatment": [
            "Rogue out and bury infected vines immediately inside sealed bags",
            "Hill up tubers deeply with soil to prevent rain-washed sporangia from infecting tubers",
            "Spray copper hydroxide proactively before cold misty rains"
        ],
        "chemical_treatment": [
            "Spray Cymoxanil 8% + Mancozeb 64% WP @ 2.5g/L or Metalaxyl-M + Mancozeb (Ridomil Gold) @ 2.5g/L",
            "Apply Dimethomorph 50% WP @ 1g/L for curative systemic control"
        ],
        "outbreak_risk": "EXTREME CRITICAL (can destroy entire potato field within 48-72 hours under cool wet weather)",
        "neighbor_alert": "EMERGENCY LATE BLIGHT EPIDEMIC: Phytophthora sporangia airborne across 10km radius. All potato/tomato farmers must spray systemic fungicide immediately.",
        "hindi_summary": "आलू में पछेती झुलसा (लेट ब्लाइट) का भीषण प्रकोप है! 48 घंटे में पूरी फसल नष्ट हो सकती है। तुरंत रिडोमिल गोल्ड या साइमोक्सानिल का छिड़काव करें।"
    },
    "Potato___healthy": {
        "crop": "Potato",
        "disease": "Healthy Potato Foliage",
        "pathogen_type": "None",
        "leaf_morphology": "Pinnate compound leaves with ovate leaflets",
        "color_signature": "Lush vibrant green",
        "lesion_pattern": "Clean green leaflets free of concentric spots, water-soaking, or white mildew",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Maintain healthy hilling and balanced potassium nutrition."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Potato foliage is healthy and vigorous.",
        "hindi_summary": "आलू के पौधे पूरी तरह स्वस्थ हैं।"
    },

    # ==================== RASPBERRY ====================
    "Raspberry___healthy": {
        "crop": "Raspberry",
        "disease": "Healthy Raspberry Foliage",
        "pathogen_type": "None",
        "leaf_morphology": "Pinnately compound 3-5 leaflets with serrated margins and whitish underside",
        "color_signature": "Rich green upper surface with silver-white hairy underside",
        "lesion_pattern": "Intact healthy leaflets with sharp serrations and no rust or cane spots",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Prune spent 2nd-year floricanes right at ground level after fruiting."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Raspberry canes are clean and productive.",
        "hindi_summary": "रास्पबेरी के पौधे स्वस्थ हैं।"
    },

    # ==================== SOYBEAN ====================
    "Soybean___Brown_spot": {
        "crop": "Soybean",
        "disease": "Soybean Brown Spot / Septoria Spot (Septoria glycines)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Trifoliate compound leaves with ovate to lanceolate leaflets",
        "color_signature": "Small angular dark brown to red spots surrounded by chlorotic yellow halos",
        "lesion_pattern": "Small (2-5mm) angular irregular brown to bronze lesions on lower canopy; leaves turn yellow and drop early",
        "is_healthy": False,
        "severity": "Moderate to High",
        "organic_treatment": [
            "Rotate crops with non-legume crops (corn, sorghum) for 1-2 seasons",
            "Plow crop residue deep after harvest to decompose fungal pycnidia",
            "Plant high-nodulation certified disease-free seeds"
        ],
        "chemical_treatment": [
            "Spray Pyraclostrobin 20% WG @ 1g/L or Azoxystrobin + Difenoconazole @ 1ml/L at R3 (pod initiation) stage",
            "Apply Carbendazim 12% + Mancozeb 63% WP (Saaf) @ 2g/L"
        ],
        "outbreak_risk": "High during warm wet monsoon periods with frequent rain splash",
        "neighbor_alert": "Soybean Brown Spot (Septoria) active on lower canopy. If spots spread upward to R3 pod level, spray protective fungicide.",
        "hindi_summary": "सोयाबीन की पत्ती पर सेप्टोरिया ब्राउन स्पॉट (पीले घेरे वाले छोटे कोणीय भूरे-लाल धब्बे) हैं। कार्बेन्डाजिम + मैनकोजेब (साफ) का छिड़काव करें।"
    },
    "Soybean___Rust": {
        "crop": "Soybean",
        "disease": "Asian Soybean Rust (Phakopsora pachyrhizi)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Trifoliate compound leaves with ovate leaflets",
        "color_signature": "Tan to reddish-brown tiny raised pustules on leaf underside",
        "lesion_pattern": "Volcano-like raised uredinial pustules packed with powdery spores causing rapid premature defoliation",
        "is_healthy": False,
        "severity": "Critical",
        "organic_treatment": [
            "Early planting of early-maturing cultivars to avoid peak spore winds",
            "Spray neem seed kernel extract (NSKE 5%) as preventive deterrent"
        ],
        "chemical_treatment": [
            "Apply Tebuconazole 25.9% EC @ 1ml/L or Hexaconazole 5% EC @ 1.5ml/L at first detection of rust pustules"
        ],
        "outbreak_risk": "High to Critical (windborne spores rapidly defoliate entire soybean belts)",
        "neighbor_alert": "SOYBEAN RUST WARNING: Airborne urediniospores detected. Adjacent fields must monitor undersides of lower leaves.",
        "hindi_summary": "सोयाबीन में रस्ट (जंग) रोग के भूरे फफोले हैं। टेबुकोनाजोल का तुरंत छिड़काव करें।"
    },
    "Soybean___healthy": {
        "crop": "Soybean",
        "disease": "Healthy Soybean Foliage",
        "pathogen_type": "None",
        "leaf_morphology": "Trifoliate ovate leaves with prominent netted veins",
        "color_signature": "Lush vibrant green",
        "lesion_pattern": "Unblemished green leaf surface with active nitrogen-fixing vigor",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Rhizobium seed inoculation and balanced phosphorus application."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Soybean crop is healthy and green.",
        "hindi_summary": "सोयाबीन की फसल पूरी तरह स्वस्थ और हरी-भरी है।"
    },

    # ==================== SQUASH & CUCURBITS ====================
    "Squash___Powdery_mildew": {
        "crop": "Squash / Cucurbits",
        "disease": "Cucurbit Powdery Mildew (Podosphaera xanthii)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Broad palmately lobed leaves with rough prickly hairs",
        "color_signature": "White talcum powder-like patches covering both leaf surfaces",
        "lesion_pattern": "Round white powdery colonies coalescing to blanket the entire leaf blade; leaves yellow and dry crisp",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Spray milk-water solution (40% cow milk, 60% water) in direct sunlight",
            "Spray potassium bicarbonate (3-5g/L) with horticultural oil"
        ],
        "chemical_treatment": [
            "Apply Myclobutanil 10% WP @ 0.5g/L or Penconazole 10% EC @ 0.5ml/L"
        ],
        "outbreak_risk": "High in dry warm weather with high relative humidity at night",
        "neighbor_alert": "Powdery mildew spreading rapidly across squash/pumpkin vines.",
        "hindi_summary": "कद्दू/लौकी की पत्ती पर सफेद पाउडर (पाउडरी मिल्ड्यू) जमा है। पोटेशियम बाइकार्बोनेट या माइक्लोबुटानिल का छिड़काव करें।"
    },

    # ==================== STRAWBERRY ====================
    "Strawberry___Leaf_scorch": {
        "crop": "Strawberry",
        "disease": "Strawberry Leaf Scorch (Diplocarpon earlianum)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Trifoliate leaves with sharp serrated margins",
        "color_signature": "Dark purple to reddish-brown blotches without light center",
        "lesion_pattern": "Irregular purplish-black blotches that coalesce; leaf edges curl up and appear scorched/burnt",
        "is_healthy": False,
        "severity": "Moderate to High",
        "organic_treatment": [
            "Remove and destroy severely scorched leaves after harvest",
            "Avoid overhead irrigation; use drip tape beneath plastic mulch"
        ],
        "chemical_treatment": [
            "Spray Captan 50% WP @ 2.5g/L or Thiophanate-methyl 70% WP @ 1g/L"
        ],
        "outbreak_risk": "High in prolonged wet conditions",
        "neighbor_alert": "Leaf scorch fungus active in strawberry beds. Water at soil level only.",
        "hindi_summary": "स्ट्रॉबेरी की पत्तियों के किनारे झुलसे और बैंगनी-काले हो रहे हैं। कैप्टन या थायोफैनेट-मिथाइल का छिड़काव करें।"
    },
    "Strawberry___Leaf_spot": {
        "crop": "Strawberry",
        "disease": "Strawberry Common Leaf Spot (Mycosphaerella fragariae)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Trifoliate leaves with deeply serrated teeth along edges",
        "color_signature": "Small circular spots with white to ash-gray centers and dark purple-red halos",
        "lesion_pattern": "Classic 'bird's eye' spots (3-6mm) with pale whitish necrotic centers bordered by deep reddish-purple margins",
        "is_healthy": False,
        "severity": "Moderate to High",
        "organic_treatment": [
            "Mow and collect old infected foliage immediately after renovation",
            "Ensure wide spacing (30cm) between crowns for rapid leaf drying"
        ],
        "chemical_treatment": [
            "Spray Copper Hydroxide @ 2g/L or Azoxystrobin @ 1ml/L at early vegetative stage",
            "Apply Difenoconazole 25% EC @ 0.5ml/L if leaf spotting exceeds 5% of canopy"
        ],
        "outbreak_risk": "High (spores splash from infected crown and soil during rain or overhead watering)",
        "neighbor_alert": "Strawberry Common Leaf Spot ('bird's eye') detected. Neighboring berry growers should avoid overhead sprinkler watering.",
        "hindi_summary": "स्ट्रॉबेरी की पत्ती पर लाल-बैंगनी घेरे वाले सफेद केंद्र के गोल धब्बे (बर्ड्स आई लीफ स्पॉट) हैं। कॉपर या डाइफेनोकोनाजोल का छिड़काव करें।"
    },
    "Strawberry___healthy": {
        "crop": "Strawberry",
        "disease": "Healthy Strawberry Foliage",
        "pathogen_type": "None",
        "leaf_morphology": "Trifoliate compound leaves with distinct serrations",
        "color_signature": "Glossy vibrant emerald green",
        "lesion_pattern": "Supple serrated leaflets completely free of purple spots, scorch, or powder",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Maintain straw mulch and clean drip irrigation."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Strawberry crowns and foliage are in peak health.",
        "hindi_summary": "स्ट्रॉबेरी के पौधे पूरी तरह स्वस्थ और फलने-फूलने के लिए तैयार हैं।"
    },

    # ==================== TOMATO (10 Classes) ====================
    "Tomato___Bacterial_spot": {
        "crop": "Tomato",
        "disease": "Tomato Bacterial Spot (Xanthomonas perforans)",
        "pathogen_type": "Bacterial",
        "leaf_morphology": "Compound pinnate leaves with lobed/serrated leaflets",
        "color_signature": "Small dark brown to black circular lesions with greasy translucent halos",
        "lesion_pattern": "Numerous small (under 3mm) dark greasy specks; lesions may tear giving leaf a ragged shot-hole look",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Apply copper octanoate or fixed copper + mancozeb tank mix",
            "Sanitize trellising stakes and tools with 10% bleach solution"
        ],
        "chemical_treatment": [
            "Spray Copper Oxychloride 50% WP @ 2.5g/L + Streptocycline @ 100ppm every 7 days"
        ],
        "outbreak_risk": "High in warm wet stormy weather",
        "neighbor_alert": "Bacterial spot on tomato foliage. Do not cultivate or harvest while foliage is wet.",
        "hindi_summary": "टमाटर की पत्ती पर छोटे काले चिकने धब्बे (बैक्टीरियल स्पॉट) हैं। कॉपर ऑक्सीक्लोराइड + स्ट्रेप्टोसाइक्लिन का छिड़काव करें।"
    },
    "Tomato___Early_blight": {
        "crop": "Tomato",
        "disease": "Tomato Early Blight (Alternaria solani)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Compound pinnate leaves",
        "color_signature": "Dark brown circular spots with concentric target rings (bullseye)",
        "lesion_pattern": "Target-board concentric rings surrounded by yellow chlorotic halo, starting on lower mature leaves",
        "is_healthy": False,
        "severity": "Moderate to High",
        "organic_treatment": [
            "Prune lowest leaves touching the ground to break splash transmission",
            "Apply thick organic straw mulch around plant base"
        ],
        "chemical_treatment": [
            "Spray Mancozeb 75% WP @ 2.5g/L or Chlorothalonil 75% WP @ 2g/L",
            "Apply Tebuconazole 25.9% EC @ 1ml/L for curative systemic control"
        ],
        "outbreak_risk": "Moderate to High",
        "neighbor_alert": "Early blight bullseye lesions progressing up tomato canopy.",
        "hindi_summary": "टमाटर के निचले पत्तों पर छल्लेदार (बुलआई) धब्बे हैं। नीचे की पत्तियां काटें और मैनकोजेब का छिड़काव करें।"
    },
    "Tomato___Late_blight": {
        "crop": "Tomato",
        "disease": "Tomato Late Blight (Phytophthora infestans)",
        "pathogen_type": "Oomycete",
        "leaf_morphology": "Compound pinnate leaves",
        "color_signature": "Water-soaked irregular pale green to dark purplish-black greasy lesions",
        "lesion_pattern": "Rapidly spreading large dark water-soaked patches; white fuzzy mold on leaf undersides during moist cool mornings",
        "is_healthy": False,
        "severity": "Critical",
        "organic_treatment": [
            "Uproot and destroy heavily infected vines in airtight plastic sacks",
            "Avoid wet leaf canopies; use drip irrigation strictly"
        ],
        "chemical_treatment": [
            "Spray Metalaxyl-M + Mancozeb (Ridomil Gold) @ 2.5g/L or Cymoxanil + Mancozeb @ 2.5g/L",
            "Apply Dimethomorph 50% WP @ 1g/L"
        ],
        "outbreak_risk": "EXTREME CRITICAL (can wipe out tomato field in 48-72 hours)",
        "neighbor_alert": "CRITICAL LATE BLIGHT EPIDEMIC: Neighboring plots must spray protective systemic fungicide immediately.",
        "hindi_summary": "टमाटर में पछेती झुलसा (लेट ब्लाइट) का गंभीर खतरा है! तुरंत रिडोमिल गोल्ड या साइमोक्सानिल का छिड़काव करें।"
    },
    "Tomato___Leaf_Mold": {
        "crop": "Tomato",
        "disease": "Tomato Leaf Mold (Passalora fulva)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Compound pinnate leaves",
        "color_signature": "Pale yellow chlorotic blotches on upper surface; velvety olive-brown mold beneath",
        "lesion_pattern": "Diffuse pale yellow spots on upper leaf surface corresponding to olive-green to brown velvety sporulation underneath",
        "is_healthy": False,
        "severity": "Moderate",
        "organic_treatment": [
            "Increase greenhouse / polytunnel ventilation to drop relative humidity below 85%",
            "Apply copper soap or potassium bicarbonate"
        ],
        "chemical_treatment": [
            "Spray Difenoconazole 25% EC @ 0.5ml/L or Azoxystrobin @ 1ml/L"
        ],
        "outbreak_risk": "High in humid, poorly ventilated polyhouses",
        "neighbor_alert": "Leaf mold spores proliferating in humid greenhouses.",
        "hindi_summary": "टमाटर की पत्ती के ऊपर पीलापन और नीचे मखमली भूरा फफूंद (लीफ मोल्ड) है। हवा का संचार बढ़ाएं और डाइफेनोकोनाजोल छिड़कें।"
    },
    "Tomato___Septoria_leaf_spot": {
        "crop": "Tomato",
        "disease": "Septoria Leaf Spot (Septoria lycopersici)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Compound pinnate leaves with serrated margins",
        "color_signature": "Small circular spots with ash-gray centers and dark brown margins",
        "lesion_pattern": "Numerous small (1.5 - 3mm) round spots with pale gray centers containing tiny black speck pycnidia",
        "is_healthy": False,
        "severity": "Moderate to High",
        "organic_treatment": [
            "Strip off infected lower leaves and discard away from tomato field",
            "Maintain 3-year solanaceous crop rotation"
        ],
        "chemical_treatment": [
            "Spray Mancozeb 75% WP @ 2.5g/L or Chlorothalonil 75% WP @ 2g/L every 7-10 days"
        ],
        "outbreak_risk": "High in wet, rainy conditions",
        "neighbor_alert": "Septoria leaf spot advancing upward from lower canopy.",
        "hindi_summary": "टमाटर के पत्तों पर भूरे घेरे वाले छोटे गोल धब्बे (सेप्टोरिया लीफ स्पॉट) हैं। निचली पत्तियां हटाएं और मैनकोजेब छिड़कें।"
    },
    "Tomato___Spider_mites_Two-spotted_spider_mite": {
        "crop": "Tomato",
        "disease": "Two-Spotted Spider Mites (Tetranychus urticae)",
        "pathogen_type": "Arachnid Pest",
        "leaf_morphology": "Compound pinnate leaves",
        "color_signature": "Fine yellow stippling, speckling, and bronzing on upper leaf surface",
        "lesion_pattern": "Dense yellow stippled pinpricks; fine silky webbing visible on leaf undersides and leaf axils",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Release predatory mites (Phytoseiulus persimilis)",
            "Spray neem oil 1% or insecticidal soap under high pressure beneath leaves"
        ],
        "chemical_treatment": [
            "Apply Spiromesifen 22.9% SC @ 1ml/L or Propargite 57% EC @ 2ml/L"
        ],
        "outbreak_risk": "High in hot, dry, dusty weather",
        "neighbor_alert": "Spider mite webbing and bronzing exploding in dry hot weather.",
        "hindi_summary": "टमाटर की पत्ती पर बारीक पीलापन और जाला (मकड़ी/माइट्स) है। स्पाइरोमेसिफेन या नीम तेल का छिड़काव करें।"
    },
    "Tomato___Target_Spot": {
        "crop": "Tomato",
        "disease": "Tomato Target Spot (Corynespora cassiicola)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Compound pinnate leaves",
        "color_signature": "Brown pinpoint spots expanding to circular lesions with light brown centers",
        "lesion_pattern": "Target-like circular lesions with subtle concentric rings and distinct yellow halos",
        "is_healthy": False,
        "severity": "Moderate",
        "organic_treatment": ["Improve plant spacing for airflow; prune lower leaves."],
        "chemical_treatment": ["Spray Azoxystrobin + Difenoconazole @ 1ml/L or Boscalid @ 0.5g/L."],
        "outbreak_risk": "Moderate",
        "neighbor_alert": "Target spot lesions spreading in tomato canopy.",
        "hindi_summary": "टमाटर पर टारगेट स्पॉट (हल्के भूरे केंद्र वाले गोल धब्बे) हैं। एजॉक्सीस्ट्रोबिन का छिड़काव करें।"
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "crop": "Tomato",
        "disease": "Tomato Yellow Leaf Curl Virus (TYLCV)",
        "pathogen_type": "Viral (Vector: Bemisia tabaci Whitefly)",
        "leaf_morphology": "Severely stunted, cupped, and distorted leaflets",
        "color_signature": "Intense interveinal chlorosis and yellow margins",
        "lesion_pattern": "Upward curling and cupping of leaflets, reduced leaflet size, bushy stunted plant habit",
        "is_healthy": False,
        "severity": "Critical",
        "organic_treatment": [
            "Install yellow sticky traps (10-15 traps per acre) to catch whiteflies",
            "Spray neem seed kernel extract (NSKE 5%) or fish oil soap",
            "Rogue out and destroy infected viral plants immediately"
        ],
        "chemical_treatment": [
            "Control whitefly vector: Spray Diafenthiuron 50% WP @ 1.2g/L or Acetamiprid 20% SP @ 0.3g/L"
        ],
        "outbreak_risk": "Critical (whiteflies rapidly transmit virus across entire tomato clusters)",
        "neighbor_alert": "WHITEFLY / TYLCV OUTBREAK: Yellow leaf curl virus spreading via whiteflies. Install yellow sticky traps immediately.",
        "hindi_summary": "टमाटर में पत्ती मरोड़ रोग (लीफ कर्ल वायरस) है जो सफेद मक्खी से फैलता है। सफेद मक्खी को रोकने के लिए डायफेंथियूरॉन या एसिटामिप्रिड छिड़कें।"
    },
    "Tomato___Tomato_mosaic_virus": {
        "crop": "Tomato",
        "disease": "Tomato Mosaic Virus (ToMV)",
        "pathogen_type": "Viral (Mechanically Transmitted)",
        "leaf_morphology": "Distorted, blistered, strap-like 'shoestring' leaflets",
        "color_signature": "Mottled pattern of alternating light and dark green patches",
        "lesion_pattern": "Mosaic mottle of dark and light green islands, blistering of leaf surface, stunted growth",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Wash hands and dip tools in non-fat dry milk solution (20%) before handling plants",
            "Never use tobacco products near tomato crops"
        ],
        "chemical_treatment": ["No chemical cure exists for viral diseases; manage vector and sanitation."],
        "outbreak_risk": "High via mechanical transmission (workers, tools, pruning)",
        "neighbor_alert": "Mosaic virus detected. Sanitize hands and tools between handling tomato beds.",
        "hindi_summary": "टमाटर में मोजेक वायरस (पत्तियों पर हरा-पीला चितकबरापन) है। रोगी पौधे उखाड़कर नष्ट करें और औजारों को साफ रखें।"
    },
    "Tomato___healthy": {
        "crop": "Tomato",
        "disease": "Healthy Tomato Foliage",
        "pathogen_type": "None",
        "leaf_morphology": "Compound pinnate leaves with healthy serrated leaflets",
        "color_signature": "Deep uniform lush green",
        "lesion_pattern": "Firm supple leaflets with no spots, yellow halos, curling, or mildew",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Balanced vermicompost, consistent trellising, and regular drip irrigation."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Tomato crop is healthy and flourishing.",
        "hindi_summary": "टमाटर की पत्तियां पूरी तरह स्वस्थ और हरी हैं।"
    },

    # ==================== COFFEE ====================
    "Coffee___Leaf_rust": {
        "crop": "Coffee",
        "disease": "Coffee Leaf Rust (Hemileia vastatrix)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Opposite, glossy, oval to elliptical leaves with undulating margins",
        "color_signature": "Bright yellow-orange powdery pustules on underside; chlorotic spots on top",
        "lesion_pattern": "Circular yellow spots on upper surface; matching powdery orange-yellow spore pustules on the lower surface causing massive defoliation",
        "is_healthy": False,
        "severity": "Critical",
        "organic_treatment": [
            "Apply Bordeaux mixture (1% or 0.5%) before pre-monsoon showers and after monsoon",
            "Regulate shade trees to maintain 40-50% filtered sunlight",
            "Plant rust-resistant Arabica/Robusta cultivars (e.g., Catimor, Castillo, Chandragiri)"
        ],
        "chemical_treatment": [
            "Spray Copper Oxychloride 50% WP @ 2.5g/L as preventive contact shield",
            "Apply Epoxiconazole + Pyraclostrobin @ 1ml/L or Hexaconazole 5% EC @ 2ml/L for systemic cure"
        ],
        "outbreak_risk": "EXTREME CRITICAL (world's most destructive coffee pathogen, easily wind-blown)",
        "neighbor_alert": "COFFEE RUST EPIDEMIC ALERT: Hemileia vastatrix pustules sporulating. Neighboring coffee estates must apply Bordeaux mixture immediately.",
        "hindi_summary": "कॉफी की पत्ती के नीचे चमकीले पीले-नारंगी पाउडर जैसे जंग के धब्बे (कॉफी लीफ रस्ट - हेमिलिया वास्टेट्रिक्स) हैं। तुरंत बोर्डो मिश्रण या हेक्साकोनाजोल का छिड़काव करें।"
    },
    "Coffee___Brown_eye_spot": {
        "crop": "Coffee",
        "disease": "Coffee Brown Eye Spot / Cercospora (Cercospora coffeicola)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Glossy oval leaves with pointed tips",
        "color_signature": "Circular brown spots with light grayish centers and brilliant yellow halo",
        "lesion_pattern": "'Eye-like' circular spots with ash-white center, brown margin, and wide yellow halo",
        "is_healthy": False,
        "severity": "Moderate to High",
        "organic_treatment": [
            "Provide adequate shade in coffee nurseries and young plantations",
            "Apply balanced nitrogen and potassium fertilizers"
        ],
        "chemical_treatment": [
            "Spray Copper Hydroxide @ 2g/L or Carbendazim 50% WP @ 1g/L"
        ],
        "outbreak_risk": "Moderate",
        "neighbor_alert": "Cercospora eye spots spreading on coffee foliage in high sun exposure.",
        "hindi_summary": "कॉफी में भूरी आंख जैसे धब्बे (सर्कोस्पोरा) हैं। पौधों को पर्याप्त छाया दें और कॉपर का छिड़काव करें।"
    },
    "Coffee___healthy": {
        "crop": "Coffee",
        "disease": "Healthy Coffee Foliage",
        "pathogen_type": "None",
        "leaf_morphology": "Glossy dark green elliptical leaves with wavy edges",
        "color_signature": "Deep waxy emerald green",
        "lesion_pattern": "Unblemished thick waxy leaf lamina without rust pustules or eye spots",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Maintain balanced agroforestry shade cover and compost mulching."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Coffee estate foliage is lush and healthy.",
        "hindi_summary": "कॉफी के पौधे पूरी तरह स्वस्थ और चमकदार हैं।"
    },

    # ==================== RICE (PADDY) ====================
    "Rice___Blast": {
        "crop": "Rice (Paddy)",
        "disease": "Rice Blast (Magnaporthe oryzae / Pyricularia oryzae)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Long slender monocot blades with parallel veins and ligule",
        "color_signature": "Spindle-shaped / diamond-shaped lesions with ash-gray center and brown border",
        "lesion_pattern": "Classic eye-shaped or spindle lesions with pointed ends, gray center, and reddish-brown margin",
        "is_healthy": False,
        "severity": "Critical",
        "organic_treatment": [
            "Seed treatment with Pseudomonas fluorescens @ 10g/kg",
            "Avoid excessive nitrogen fertilizer application; split nitrogen into 3-4 doses"
        ],
        "chemical_treatment": [
            "Spray Tricyclazole 75% WP @ 0.6g/L or Isoprothiolane 40% EC @ 1.5ml/L",
            "Apply Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1ml/L"
        ],
        "outbreak_risk": "Critical in high humidity (>90%) with cool night temperatures (20-24°C)",
        "neighbor_alert": "RICE BLAST EPIDEMIC ALERT: Spindle lesions detected. Neighboring paddy fields must apply Tricyclazole immediately.",
        "hindi_summary": "धान (चावल) में ब्लास्ट रोग (आंख/नाव के आकार के धब्बे) है। ट्राइसाइक्लाजोल या आइसोप्रोपियोलेन का तुरंत छिड़काव करें।"
    },
    "Rice___Bacterial_leaf_blight": {
        "crop": "Rice (Paddy)",
        "disease": "Rice Bacterial Leaf Blight (Xanthomonas oryzae pv. oryzae)",
        "pathogen_type": "Bacterial",
        "leaf_morphology": "Long slender monocot blades",
        "color_signature": "Water-soaked stripes turning wavy yellowish-white bleached lesions along leaf margins",
        "lesion_pattern": "Lesions begin at tip/margins as wavy yellowish-white stripes; leaves dry and look bleached white",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Drain standing water temporarily for 2-3 days to lower humidity",
            "Avoid top-dressing nitrogen when blight is active"
        ],
        "chemical_treatment": [
            "Spray Copper Oxychloride 50% WP @ 2.5g/L + Streptocycline @ 100ppm"
        ],
        "outbreak_risk": "High during monsoons and typhoons with strong winds",
        "neighbor_alert": "Bacterial blight spreading through irrigation water across paddy terraces.",
        "hindi_summary": "धान में जीवाणु झुलसा (किनारों से सूखती सफेद पत्तियां) है। कॉपर और स्ट्रेप्टोसाइक्लिन का छिड़काव करें और पानी निकालें।"
    },
    "Rice___Brown_spot": {
        "crop": "Rice (Paddy)",
        "disease": "Rice Brown Spot (Bipolaris oryzae)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Long slender monocot blades",
        "color_signature": "Oval to circular brown spots with dark brown halo and gray center",
        "lesion_pattern": "Uniformly distributed sesame-seed sized spots on leaf lamina; associated with nutrient-deficient soil",
        "is_healthy": False,
        "severity": "Moderate to High",
        "organic_treatment": [
            "Apply balanced potassium and silicon fertilizer to strengthen leaf cuticle",
            "Seed treatment with Trichoderma viride @ 5g/kg"
        ],
        "chemical_treatment": [
            "Spray Mancozeb 75% WP @ 2g/L or Propiconazole 25% EC @ 1ml/L"
        ],
        "outbreak_risk": "Moderate",
        "neighbor_alert": "Brown spot active in paddy fields. Check soil fertility and apply potash.",
        "hindi_summary": "धान की पत्ती पर भूरे तिल जैसे धब्बे हैं। पोटाश खाद डालें और मैनकोजेब या प्रोपिकोनाजोल छिड़कें।"
    },
    "Rice___Leaf_smut": {
        "crop": "Rice (Paddy)",
        "disease": "Rice Leaf Smut (Entyloma oryzae)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Long slender monocot blades with parallel veins",
        "color_signature": "Small slightly raised angular black or dark brown spots on both leaf surfaces",
        "lesion_pattern": "Short linear to rectangular black smut sori (0.5-5mm) scattered between veins; leaf tips turn yellow and dry",
        "is_healthy": False,
        "severity": "Moderate",
        "organic_treatment": [
            "Avoid excessive nitrogen top-dressing late in the vegetative stage",
            "Remove and compost crop stubble deeply after harvest to reduce teliospores"
        ],
        "chemical_treatment": [
            "Usually minor; if severe on upper leaves, spray Propiconazole 25% EC @ 1ml/L or Copper Oxychloride 50% WP @ 2.5g/L"
        ],
        "outbreak_risk": "Moderate in humid late-season paddy fields",
        "neighbor_alert": "Rice Leaf Smut detected. Keep nitrogen balanced and inspect flag leaves.",
        "hindi_summary": "धान की पत्ती पर छोटे काले उभरे हुए धब्बे (लीफ स्मट) हैं। यूरिया/नाइट्रोजन की अधिक मात्रा न दें और जरूरत हो तो प्रोपिकोनाजोल छिड़कें।"
    },
    "Rice___healthy": {
        "crop": "Rice (Paddy)",
        "disease": "Healthy Rice Foliage",
        "pathogen_type": "None",
        "leaf_morphology": "Long erect emerald green blades",
        "color_signature": "Vibrant emerald green",
        "lesion_pattern": "Clean upright blades with clear parallel venation and no spindle lesions or bleached margins",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Maintain balanced water management and Azospirillum biofertilizer."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Paddy crop is robust and healthy.",
        "hindi_summary": "धान की फसल पूरी तरह हरी और स्वस्थ है।"
    },

    # ==================== WHEAT ====================
    "Wheat___Yellow_stripe_rust": {
        "crop": "Wheat",
        "disease": "Yellow Stripe Rust (Puccinia striiformis)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Slender linear monocot blades with parallel veins",
        "color_signature": "Bright yellow-orange powdery pustules arranged in continuous narrow stripes",
        "lesion_pattern": "Narrow linear stripes of lemon-yellow powdery uredinia running parallel to veins along entire leaf blade",
        "is_healthy": False,
        "severity": "Critical",
        "organic_treatment": [
            "Plant rust-resistant wheat varieties (e.g., HD 2967, HD 3086, DBW 187)",
            "Early sowing in November to bypass cool humid rust peaks"
        ],
        "chemical_treatment": [
            "Spray Propiconazole 25% EC (Tilt) @ 1ml/L or Tebuconazole 25.9% EC @ 1ml/L immediately at first yellow stripe"
        ],
        "outbreak_risk": "EXTREME CRITICAL (windblown spores travel hundreds of miles overnight)",
        "neighbor_alert": "YELLOW RUST EPIDEMIC ALERT: Puccinia striiformis detected. All wheat plots in the block must spray Propiconazole.",
        "hindi_summary": "गेहूं की पत्ती पर चमकीली पीली धारियों में जंग (पीला रतुआ) है। तुरंत प्रोपिकोनाजोल (टिल्ट) का 1 मिली/लीटर पानी में छिड़काव करें।"
    },
    "Wheat___Brown_leaf_rust": {
        "crop": "Wheat",
        "disease": "Brown / Leaf Rust (Puccinia triticina)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Slender linear monocot blades",
        "color_signature": "Small round to oval orange-brown scattered pustules",
        "lesion_pattern": "Scattered round orange-brown pustules randomly distributed across upper leaf surface (not in linear stripes)",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": ["Early crop sowing and balanced N-P-K fertilization."],
        "chemical_treatment": ["Spray Propiconazole 25% EC @ 1ml/L or Mancozeb 75% WP @ 2.5g/L."],
        "outbreak_risk": "High in warm (20-25°C) humid weather",
        "neighbor_alert": "Brown leaf rust detected on wheat flag leaves.",
        "hindi_summary": "गेहूं पर भूरा रतुआ (बिखरे हुए नारंगी-भूरे फफोले) है। प्रोपिकोनाजोल या मैनकोजेब का छिड़काव करें।"
    },
    "Wheat___Septoria_tritici_blotch": {
        "crop": "Wheat",
        "disease": "Wheat Septoria Tritici Blotch (Zymoseptoria tritici)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Slender linear monocot blades with parallel veins",
        "color_signature": "Irregular tan-brown elongated blotches studded with tiny black pycnidia specks",
        "lesion_pattern": "Oval to elongated yellow-brown lesions limited by leaf veins containing rows of pinpoint black fruiting bodies",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Rotate wheat with non-cereal crops and plow under infected straw residue",
            "Avoid excessive early nitrogen fertilization that creates dense humid canopies"
        ],
        "chemical_treatment": [
            "Spray Azoxystrobin + Propiconazole @ 1ml/L or Tebuconazole 25.9% EC @ 1ml/L at flag leaf emergence"
        ],
        "outbreak_risk": "High in cool wet windy spring/winter weather",
        "neighbor_alert": "Septoria blotch active on wheat leaves. Protect flag leaf before ear emergence.",
        "hindi_summary": "गेहूं की पत्ती पर काले बिंदुओं वाले लंबे भूरे धब्बे (सेप्टोरिया ब्लॉच) हैं। टेबुकोनाजोल या प्रोपिकोनाजोल का छिड़काव करें।"
    },
    "Wheat___healthy": {
        "crop": "Wheat",
        "disease": "Healthy Wheat Foliage",
        "pathogen_type": "None",
        "leaf_morphology": "Slender erect green linear blades",
        "color_signature": "Deep vibrant green",
        "lesion_pattern": "Clean flag leaves with no rust stripes, powdery mold, or necrotic tips",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Ensure timely irrigation at CRI and flowering stages."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Wheat crop is healthy and vigorous.",
        "hindi_summary": "गेहूं की फसल स्वस्थ और हरी है।"
    },

    # ==================== COTTON ====================
    "Cotton___Leaf_curl_virus": {
        "crop": "Cotton",
        "disease": "Cotton Leaf Curl Virus (CLCuD / CLCuV)",
        "pathogen_type": "Viral (Vector: Bemisia tabaci Whitefly)",
        "leaf_morphology": "Palmately 3-5 lobed leaves",
        "color_signature": "Dark green thickened veins; upward or downward leaf curling",
        "lesion_pattern": "Upward or downward cupping of leaves, prominent thickening of main veins, and cup-shaped leaf enations on underside",
        "is_healthy": False,
        "severity": "Critical",
        "organic_treatment": [
            "Install yellow sticky cards (15 per acre) for whitefly mass trapping",
            "Spray neem seed kernel extract (NSKE 5%) or castor oil barrier borders",
            "Uproot and destroy early infected plants"
        ],
        "chemical_treatment": [
            "Control whitefly vector: Spray Diafenthiuron 50% WP @ 1.2g/L or Pyriproxyfen 10% EC @ 2ml/L"
        ],
        "outbreak_risk": "Critical across cotton growing regions",
        "neighbor_alert": "COTTON LEAF CURL VIRUS ALERT: Whitefly populations transmitting CLCuD. Control vectors immediately.",
        "hindi_summary": "कपास में पत्ता मरोड़ (लीफ कर्ल वायरस) रोग है। सफेद मक्खी को मारने के लिए डायफेंथियूरॉन का छिड़काव करें।"
    },
    "Cotton___Bacterial_blight": {
        "crop": "Cotton",
        "disease": "Cotton Bacterial Blight / Angular Leaf Spot (Xanthomonas citri pv. malvacearum)",
        "pathogen_type": "Bacterial",
        "leaf_morphology": "Palmately lobed cotton leaves",
        "color_signature": "Small angular water-soaked spots turning dark brown/black",
        "lesion_pattern": "Lesions are sharply delimited by veinlets giving an angular geometric appearance; black arm on stems",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Acid delinting of cottonseed with sulfuric acid before planting",
            "Remove and destroy infected plant debris"
        ],
        "chemical_treatment": [
            "Spray Copper Oxychloride 50% WP @ 2.5g/L + Streptocycline @ 100ppm"
        ],
        "outbreak_risk": "High in stormy wet weather",
        "neighbor_alert": "Angular leaf spot detected in cotton fields.",
        "hindi_summary": "कपास में कोणीय पत्ती धब्बा (बैक्टीरियल ब्लाइट) है। कॉपर ऑक्सीक्लोराइड + स्ट्रेप्टोसाइक्लिन का छिड़काव करें।"
    },
    "Cotton___healthy": {
        "crop": "Cotton",
        "disease": "Healthy Cotton Foliage",
        "pathogen_type": "None",
        "leaf_morphology": "Broad palmately lobed green leaves",
        "color_signature": "Lush emerald green",
        "lesion_pattern": "Supple unblemished lobed leaves with no vein thickening or angular spots",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Maintain balanced potash nutrition and regular weed control."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Cotton crop is vigorous and healthy.",
        "hindi_summary": "कपास के पौधे पूरी तरह स्वस्थ हैं।"
    },

    # ==================== BANANA ====================
    "Banana___Black_sigatoka": {
        "crop": "Banana",
        "disease": "Black Sigatoka / Black Leaf Streak (Pseudocercospora fijiensis)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Massive elongated paddle-shaped monocot leaves",
        "color_signature": "Reddish-brown narrow specks enlarging to dark brown-black spindle lesions with gray center",
        "lesion_pattern": "Parallel dark streaks coalescing into large necrotic black blotches causing massive leaf collapse",
        "is_healthy": False,
        "severity": "Critical",
        "organic_treatment": [
            "De-leaf and excise heavily infected leaf parts with clean sharp curved knives",
            "Spray mineral oil (horticultural paraffinic oil) to inhibit spore germination"
        ],
        "chemical_treatment": [
            "Spray Propiconazole 25% EC @ 1ml/L or Difenoconazole 25% EC @ 1ml/L mixed with 1% mineral oil"
        ],
        "outbreak_risk": "High in tropical warm humid plantations",
        "neighbor_alert": "Black Sigatoka spreading in banana groves. Prune dead leaves immediately.",
        "hindi_summary": "केले में सिगाटोका (काली धारियां और पत्तों का सूखना) रोग है। रोगी पत्ते काटें और प्रोपिकोनाजोल का छिड़काव करें।"
    },
    "Banana___Cordana_leaf_spot": {
        "crop": "Banana",
        "disease": "Banana Cordana Leaf Spot (Cordana musae)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Broad elongated paddle-shaped leaves",
        "color_signature": "Pale brown to grayish-tan oval spots with bright yellow halo",
        "lesion_pattern": "Large diamond/oval zonate spots with concentric pale brown rings and distinct yellow margins",
        "is_healthy": False,
        "severity": "Moderate to High",
        "organic_treatment": [
            "Remove older heavily spotted lower leaves to reduce humidity",
            "Improve plantation drainage and weed control"
        ],
        "chemical_treatment": [
            "Spray Mancozeb 75% WP @ 2.5g/L or Propiconazole 25% EC @ 1ml/L"
        ],
        "outbreak_risk": "Moderate to High during humid rainy weather",
        "neighbor_alert": "Cordana leaf spot active on banana leaves.",
        "hindi_summary": "केले की पत्ती पर पीले घेरे वाले अंडाकार भूरे धब्बे (कॉर्डाना लीफ स्पॉट) हैं। मैनकोजेब या प्रोपिकोनाजोल का छिड़काव करें।"
    },
    "Banana___Pestalotiopsis_leaf_spot": {
        "crop": "Banana",
        "disease": "Banana Pestalotiopsis Leaf Spot (Pestalotiopsis palmarum)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Broad elongated paddle-shaped leaves",
        "color_signature": "Light brown to ash-gray irregular spots with dark brown borders and tiny black dots",
        "lesion_pattern": "Irregular dry necrotic patches studded with pinpoint black fruiting bodies (acervuli)",
        "is_healthy": False,
        "severity": "Moderate",
        "organic_treatment": [
            "Prune and burn dried infected leaf blades",
            "Apply balanced potassium fertilizer to strengthen leaf tissue"
        ],
        "chemical_treatment": [
            "Spray Carbendazim 50% WP @ 1g/L or Copper Oxychloride @ 2.5g/L"
        ],
        "outbreak_risk": "Moderate",
        "neighbor_alert": "Pestalotiopsis leaf spot detected in banana plantation.",
        "hindi_summary": "केले की पत्ती पर हल्के भूरे-सलेटी धब्बे (पेस्टालोशियोप्सिस) हैं। सूखे पत्ते हटाएं और कार्बेन्डाजिम छिड़कें।"
    },
    "Banana___healthy": {
        "crop": "Banana",
        "disease": "Healthy Banana Foliage",
        "pathogen_type": "None",
        "leaf_morphology": "Broad expansive paddle-shaped green leaves",
        "color_signature": "Lush vibrant tropical green",
        "lesion_pattern": "Intact wide green lamina with no necrotic streaks or yellow borders",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Apply heavy farmyard manure compost and maintain soil drainage."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Banana plants are vigorous and healthy.",
        "hindi_summary": "केले के पत्ते पूरी तरह स्वस्थ और बड़े हैं।"
    },

    # ==================== MANGO ====================
    "Mango___Anthracnose": {
        "crop": "Mango",
        "disease": "Mango Anthracnose (Colletotrichum gloeosporioides)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Oblong lanceolate leaves with leathery texture",
        "color_signature": "Irregular dark brown to black necrotic lesions with yellow margins",
        "lesion_pattern": "Circular to angular dark brown spots; leaf tips blighted; young leaves tear and twist ('shot-hole')",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Prune overcrowded branches to allow maximum sunlight into canopy",
            "Spray copper oxychloride (3g/L) before flowering flush"
        ],
        "chemical_treatment": [
            "Apply Azoxystrobin 23% SC @ 1ml/L or Carbendazim 50% WP @ 1g/L at new vegetative flush"
        ],
        "outbreak_risk": "High during rainy humid conditions during new flush and blossom",
        "neighbor_alert": "Anthracnose blighting new mango flush and blossoms.",
        "hindi_summary": "आम में एन्थ्रेक्नोज (काले-भूरे धब्बे और पत्तों का सूखना) है। कॉपर ऑक्सीक्लोराइड या कार्बेन्डाजिम का छिड़काव करें।"
    },
    "Mango___Bacterial_canker": {
        "crop": "Mango",
        "disease": "Mango Bacterial Canker (Xanthomonas citri pv. mangiferaeindicae)",
        "pathogen_type": "Bacterial",
        "leaf_morphology": "Oblong lanceolate leathery leaves",
        "color_signature": "Angular water-soaked dark brown/black raised spots with yellow halo",
        "lesion_pattern": "Small angular water-soaked lesions delimited by veins that turn raised, dark black, and corky",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Prune and destroy infected twigs and leaves before monsoon",
            "Spray neem oil or copper hydroxide protectively"
        ],
        "chemical_treatment": [
            "Spray Streptocycline @ 100ppm + Copper Oxychloride 50% WP @ 2.5g/L at 10-day intervals"
        ],
        "outbreak_risk": "High during wind-driven monsoon rain",
        "neighbor_alert": "Mango Bacterial Canker active. Protect young flush before rain.",
        "hindi_summary": "आम की पत्ती पर कोणीय काले उभरे धब्बे (बैक्टीरियल कैंकर) हैं। कॉपर ऑक्सीक्लोराइड + स्ट्रेप्टोसाइक्लिन का छिड़काव करें।"
    },
    "Mango___Cutting_weevil": {
        "crop": "Mango",
        "disease": "Mango Leaf Cutting Weevil (Deporaus marginatus)",
        "pathogen_type": "Insect Pest",
        "leaf_morphology": "Tender young lanceolate mango leaves",
        "color_signature": "Cleanly severed/cut leaf blades with brown drying edges",
        "lesion_pattern": "Sharp scissor-like clean cuts across tender leaf blades leaving only basal stubs",
        "is_healthy": False,
        "severity": "Moderate to High",
        "organic_treatment": [
            "Collect and destroy fallen cut leaf pieces on the orchard floor (contain weevil eggs)",
            "Spray neem seed kernel extract (NSKE 5%) on new pink flush"
        ],
        "chemical_treatment": [
            "Spray Lambda-cyhalothrin 5% EC @ 0.5ml/L or Quinalphos 25% EC @ 2ml/L on new tender flush"
        ],
        "outbreak_risk": "High during new vegetative flush",
        "neighbor_alert": "Leaf cutting weevil damaging tender mango shoots.",
        "hindi_summary": "आम की नई पत्तियों को लीफ कटिंग वीविल (कैंची की तरह कटी पत्तियां) काट रहा है। गिरी पत्तियां जलाएं और नीम या लैम्ब्डा-साइहलोथ्रिन छिड़कें।"
    },
    "Mango___Die_back": {
        "crop": "Mango",
        "disease": "Mango Die Back (Lasiodiplodia theobromae)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Lanceolate mango leaves on terminal shoots",
        "color_signature": "Browning and scorching of leaves from tip/margins downward",
        "lesion_pattern": "Leaves turn brown, curl upward, and dry out from twig tips backward; bark turns dark",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Prune 7-10 cm below the dried dead portion of twigs and apply Bordeaux paste on cut ends"
        ],
        "chemical_treatment": [
            "Spray Copper Oxychloride 50% WP @ 3g/L or Carbendazim 50% WP @ 1g/L after pruning"
        ],
        "outbreak_risk": "Moderate to High after monsoon",
        "neighbor_alert": "Mango Die Back detected; prune dead twigs and seal cuts with copper paste.",
        "hindi_summary": "आम में डाई-बैक (ऊपर से टहनियों व पत्तों का सूखना) रोग है। सूखी टहनी काटकर कॉपर पेस्ट लगाएं और कॉपर ऑक्सीक्लोराइड छिड़कें।"
    },
    "Mango___Gall_midge": {
        "crop": "Mango",
        "disease": "Mango Leaf Gall Midge (Procontarinia matteiana)",
        "pathogen_type": "Insect Pest",
        "leaf_morphology": "Oblong lanceolate mango leaves",
        "color_signature": "Raised wart-like green/brown galls or pimples across leaf surface",
        "lesion_pattern": "Small raised conical or circular galls/pustules dotting the leaf lamina; leaves deform",
        "is_healthy": False,
        "severity": "Moderate",
        "organic_treatment": [
            "Prune heavily galled leaves and improve orchard airflow",
            "Spray neem oil (5ml/L) during new leaf emergence"
        ],
        "chemical_treatment": [
            "Spray Imidacloprid 17.8% SL @ 0.5ml/L or Dimethoate 30% EC @ 2ml/L at bud burst"
        ],
        "outbreak_risk": "Moderate during new vegetative flush",
        "neighbor_alert": "Mango Gall Midge infesting new leaves.",
        "hindi_summary": "आम की पत्ती पर छोटे-छोटे उभरे हुए दाने/गांठें (गॉल मिज कीट) हैं। नई कोपल निकलते समय इमिडाक्लोप्रिड का छिड़काव करें।"
    },
    "Mango___Powdery_mildew": {
        "crop": "Mango",
        "disease": "Mango Powdery Mildew (Oidium mangiferae)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Oblong lanceolate leaves and panicles",
        "color_signature": "White grayish powdery talcum coating on upper leaf surface and shoots",
        "lesion_pattern": "White powdery fungal growth causing leaves and blossoms to curl, turn brown, and drop",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Spray wettable sulfur (2g/L) or potassium bicarbonate (3g/L)"
        ],
        "chemical_treatment": [
            "Spray Hexaconazole 5% EC @ 1ml/L or Wettable Sulfur 80% WP @ 2g/L at pre-bloom and fruit set"
        ],
        "outbreak_risk": "High in cool cloudy mornings (Feb-March)",
        "neighbor_alert": "Mango Powdery Mildew active; protect flowering panicles immediately.",
        "hindi_summary": "आम की पत्ती व बौर पर सफेद पाउडर (पाउडरी मिल्ड्यू) है। घुलनशील सल्फर या हेक्साकोनाजोल का छिड़काव करें।"
    },
    "Mango___Sooty_mould": {
        "crop": "Mango",
        "disease": "Mango Sooty Mould (Capnodium mangiferae)",
        "pathogen_type": "Fungal (Secondary to Sap-Sucking Hoppers/Scales)",
        "leaf_morphology": "Oblong lanceolate leathery leaves",
        "color_signature": "Thick velvety black soot-like coating covering upper leaf surface",
        "lesion_pattern": "Superficial black charcoal-like crust growing on honeydew secreted by mango hoppers/mealybugs",
        "is_healthy": False,
        "severity": "Moderate",
        "organic_treatment": [
            "Spray starch solution (2%) or soap-water to peel off black soot layer",
            "Control mango hoppers/mealybugs with neem oil 1%"
        ],
        "chemical_treatment": [
            "Spray Imidacloprid 17.8% SL @ 0.4ml/L (for hoppers) + Wettable Sulfur @ 2g/L"
        ],
        "outbreak_risk": "High when mango hoppers are unchecked",
        "neighbor_alert": "Sooty mould indicates active mango hopper/scale infestation.",
        "hindi_summary": "आम की पत्ती पर काली कालिख (सूटी मोल्ड) जमी है जो भुनगा कीट से होती है। इमिडाक्लोप्रिड + स्टार्च/नीम तेल का छिड़काव करें।"
    },
    "Mango___healthy": {
        "crop": "Mango",
        "disease": "Healthy Mango Foliage",
        "pathogen_type": "None",
        "leaf_morphology": "Leathery lanceolate dark green glossy leaves",
        "color_signature": "Glossy deep green",
        "lesion_pattern": "Unblemished thick leaf blades with clear midrib and no black spots or powdery mold",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Annual post-harvest canopy pruning and organic compost."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Mango trees are healthy and strong.",
        "hindi_summary": "आम के पत्ते पूरी तरह स्वस्थ और चमकदार हैं।"
    },

    # ==================== SUGARCANE ====================
    "Sugarcane___Red_rot": {
        "crop": "Sugarcane",
        "disease": "Sugarcane Red Rot (Colletotrichum falcatum)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Long arching sword-like monocot leaves with prominent white midrib",
        "color_signature": "Red lesions on midrib with dark borders; leaves wither yellow-brown from tip",
        "lesion_pattern": "Blood-red streaks studded with dark spots along the leaf midrib; whole crown withers and dries",
        "is_healthy": False,
        "severity": "Critical",
        "organic_treatment": [
            "Use certified disease-free setts treated with hot water (52°C for 30 minutes)",
            "Uproot and burn entire infected clumps immediately"
        ],
        "chemical_treatment": [
            "Sett dip in Carbendazim 50% WP @ 1g/L before planting; foliar sprays cannot cure internal vascular rot"
        ],
        "outbreak_risk": "Critical across sugarcane growing belts",
        "neighbor_alert": "RED ROT WARNING: Vascular fungal rot detected. Rogue out diseased clumps immediately.",
        "hindi_summary": "गन्ने में लाल सड़न (रेड रॉट) रोग है। बीच की नस पर लाल धब्बे दिखते हैं। रोगी पौधों को उखाड़कर नष्ट करें।"
    },
    "Sugarcane___healthy": {
        "crop": "Sugarcane",
        "disease": "Healthy Sugarcane Foliage",
        "pathogen_type": "None",
        "leaf_morphology": "Long arching sword-like green blades with white central midrib",
        "color_signature": "Deep vibrant green",
        "lesion_pattern": "Clean green blades with bright white midrib without red lesions or drying",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Adequate earthing-up and balanced fertilizer management."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Sugarcane crop is healthy.",
        "hindi_summary": "गन्ने की फसल पूरी तरह स्वस्थ और हरी है।"
    },

    # ==================== TEA ====================
    "Tea___Blister_blight": {
        "crop": "Tea",
        "disease": "Tea Blister Blight (Exobasidium vexans)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Elliptical serrated tender tea leaves",
        "color_signature": "Translucent circular spots turning into blistered white velvety concavities",
        "lesion_pattern": "Raised convex pale green blister on upper leaf surface with a corresponding white velvety concave depression beneath",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Regulate shade canopy in tea estates to allow sunlight during monsoon",
            "Harvest tender two leaves and a bud on short 5-day rounds"
        ],
        "chemical_treatment": [
            "Spray Copper Oxychloride 50% WP @ 2g/L + Hexaconazole 5% EC @ 1ml/L every 7 days during monsoon"
        ],
        "outbreak_risk": "High in mist-laden high-altitude tea gardens",
        "neighbor_alert": "Blister blight attacking tender tea flushes.",
        "hindi_summary": "चाय की पत्ती पर सफेद फफोले (ब्लिस्टर ब्लाइट) हैं। कॉपर ऑक्सीक्लोराइड + हेक्साकोनाजोल का छिड़काव करें।"
    },
    "Tea___healthy": {
        "crop": "Tea",
        "disease": "Healthy Tea Foliage",
        "pathogen_type": "None",
        "leaf_morphology": "Glossy green serrated tender leaves",
        "color_signature": "Vibrant emerald green",
        "lesion_pattern": "Clean glossy tender shoots and leaves free of blisters or red rust",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Regular plucking and balanced micronutrient foliar spray."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Tea bushes are in prime healthy flush.",
        "hindi_summary": "चाय की पत्तियां पूरी तरह स्वस्थ हैं।"
    },

    # ==================== GROUNDNUT (PEANUT) ====================
    "Groundnut___Tikka_leaf_spot": {
        "crop": "Groundnut (Peanut)",
        "disease": "Groundnut Tikka Disease / Cercospora Leaf Spot (Cercospora arachidicola / Phaeoisariopsis)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Even-pinnate leaves with 4 oval to obovate leaflets",
        "color_signature": "Circular reddish-brown to dark brown spots surrounded by bright yellow halo",
        "lesion_pattern": "Multiple small circular necrotic spots with yellow rings on leaflets, causing extensive premature leaf shedding",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Seed treatment with Trichoderma viride @ 5g/kg",
            "Spray neem seed kernel extract (NSKE 5%) before flowering"
        ],
        "chemical_treatment": [
            "Spray Mancozeb 75% WP @ 2.5g/L or Carbendazim 50% WP @ 1g/L or Hexaconazole @ 1ml/L"
        ],
        "outbreak_risk": "High in warm humid weather with rain splash",
        "neighbor_alert": "Tikka disease spreading across groundnut plots. Spray protective fungicide.",
        "hindi_summary": "मूंगफली की पत्ती पर पीले घेरे वाले गोल भूरे धब्बे (टिक्का रोग) हैं। कार्बेन्डाजिम या मैनकोजेब का छिड़काव करें।"
    },
    "Groundnut___healthy": {
        "crop": "Groundnut (Peanut)",
        "disease": "Healthy Groundnut Foliage",
        "pathogen_type": "None",
        "leaf_morphology": "Four-leaflet pinnate compound leaves",
        "color_signature": "Deep rich green",
        "lesion_pattern": "Clean unblemished oval leaflets with no tikka spots or rust pustules",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Rhizobium culture seed treatment and gypsum application at pegging."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Groundnut foliage is healthy.",
        "hindi_summary": "मूंगफली के पौधे स्वस्थ और हरे-भरे हैं।"
    },

    # ==================== MUSTARD ====================
    "Mustard___White_rust": {
        "crop": "Mustard",
        "disease": "Mustard White Rust (Albugo candida)",
        "pathogen_type": "Oomycete",
        "leaf_morphology": "Lyrate-pinnatifid large green leaves",
        "color_signature": "Prominent raised creamy-white blister-like pustules on lower leaf surface",
        "lesion_pattern": "White chalky pustules scattered on underside of leaves; floral parts swell into distorted 'staghead'",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Early sowing in October to escape cool humid infection windows",
            "Destroy wild cruciferous weed hosts"
        ],
        "chemical_treatment": [
            "Spray Metalaxyl 8% + Mancozeb 64% WP @ 2g/L or Mancozeb 75% WP @ 2.5g/L"
        ],
        "outbreak_risk": "High in foggy cold winter weather (12-18°C)",
        "neighbor_alert": "White rust blisters detected in mustard fields.",
        "hindi_summary": "सरसों की पत्ती के नीचे सफेद छाले (व्हाइट रस्ट) हैं। रिडोमिल या मैनकोजेब का छिड़काव करें।"
    },
    "Mustard___healthy": {
        "crop": "Mustard",
        "disease": "Healthy Mustard Foliage",
        "pathogen_type": "None",
        "leaf_morphology": "Broad green lobed leaves",
        "color_signature": "Lush vibrant green",
        "lesion_pattern": "Clean broad leaves free of white blisters or Alternaria concentric spots",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Proper row spacing (30x10 cm) and balanced sulfur fertilization."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Mustard crop is healthy.",
        "hindi_summary": "सरसों की फसल पूरी तरह स्वस्थ है।"
    },

    # ==================== ONION & GARLIC ====================
    "Onion___Purple_blotch": {
        "crop": "Onion",
        "disease": "Onion Purple Blotch (Alternaria porri)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Hollow cylindrical tubular leaves with waxy bloom",
        "color_signature": "Sunken purplish-brown elliptical lesions with yellow chlorotic margin",
        "lesion_pattern": "Small water-soaked areas that turn brown-purple with concentric rings; leaves break over at lesion point",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Apply neem cake in soil and spray Trichoderma harzianum",
            "Maintain wide bulb spacing to accelerate foliage drying"
        ],
        "chemical_treatment": [
            "Spray Mancozeb 75% WP @ 2.5g/L + sticker (Sandovit @ 1ml/L) or Tebuconazole @ 1ml/L"
        ],
        "outbreak_risk": "High during warm humid monsoon or post-rain periods",
        "neighbor_alert": "Purple blotch causing onion leaves to collapse. Add sticker with fungicide spray.",
        "hindi_summary": "प्याज की पत्तियों पर बैंगनी-भूरे धब्बे (पर्पल ब्लॉच) हैं। मैनकोजेब में स्टीकर मिलाकर छिड़काव करें।"
    },
    "Onion___healthy": {
        "crop": "Onion",
        "disease": "Healthy Onion Foliage",
        "pathogen_type": "None",
        "leaf_morphology": "Erect cylindrical tubular hollow green leaves",
        "color_signature": "Bluish-green with natural waxy bloom",
        "lesion_pattern": "Firm upright tubular leaves with no purple spots, thrips silvering, or tip burn",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Consistent light irrigation and balanced potassium."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Onion crop is upright and healthy.",
        "hindi_summary": "प्याज की फसल स्वस्थ और मजबूत है।"
    },

    # ==================== BEECH ====================
    "Beech___Leaf_disease": {
        "crop": "Beech",
        "disease": "Beech Leaf Disease (Litylenchus crenatae)",
        "pathogen_type": "Nematode (Foliar Nematode)",
        "leaf_morphology": "Elliptical ovate leaves with prominent parallel lateral veins and toothed margins",
        "color_signature": "Dark green, yellow, and reddish-brown interveinal banding between lateral veins",
        "lesion_pattern": "Distinctive dark thickened interveinal stripes/bands that turn yellow, orange-brown, and leathery/crinkled",
        "is_healthy": False,
        "severity": "High to Critical",
        "organic_treatment": [
            "Prune and bag heavily infected lower branches (do not compost diseased leaves on site)",
            "Maintain tree vigor with deep organic root-zone mulching and watering during drought"
        ],
        "chemical_treatment": [
            "Apply potassium phosphite (phosphonate) soil drench / trunk injection in spring to boost tree defense",
            "Targeted nematicide/miticide (e.g. fluopyram or abamectin) during late-summer nematode migration"
        ],
        "outbreak_risk": "High (foliar nematodes spread via rain splash, wind, and birds)",
        "neighbor_alert": "Beech Leaf Disease (Litylenchus crenatae) detected. Inspect nearby beech trees for dark interveinal banding.",
        "hindi_summary": "बीच (Beech) की पत्ती में बीच लीफ डिज़ीज़ (Litylenchus crenatae नेमाटोड) के लक्षण हैं — नसों के बीच गहरी पीली-भूरी धारियां दिख रही हैं। संक्रमित पत्तियां हटाकर नष्ट करें।"
    }
}


def diagnose_with_master_engine(
    vision_description: str,
    pixel_stats: Dict[str, Any],
    crop_hint: Optional[str] = "",
    farmer_notes: Optional[str] = "",
    neural_class: Optional[str] = None,
    neural_sim: float = 0.0
) -> Dict[str, Any]:
    """
    High-Precision Deterministic Agronomic Diagnostic Matcher.
    Combines MobileNetV3 deep neural embeddings trained on PlantVillage & archive.zip,
    leaf morphology, pathognomonic symptoms, and physical color signatures
    across 60+ global and Indian agricultural crops.
    """
    obs_text = f"{vision_description or ''} {farmer_notes or ''}".lower()
    clean_crop_hint = (crop_hint or "").strip()

    # 1. Botanical Leaf Morphology Clues
    is_serrated = any(w in obs_text for w in ["serrated", "tooth", "teeth", "saw", "jagged", "dentate"])
    is_lobed = any(w in obs_text for w in ["lobe", "lobed", "palmate", "webbed"])
    is_grassy = any(w in obs_text for w in ["grass", "corn", "narrow", "parallel", "maize", "strap", "linear", "blade", "paddy", "rice", "wheat"])
    is_trifoliate = any(w in obs_text for w in ["trifoliate", "three", "3 leaf", "three leaflets"])
    is_oval_waxy = any(w in obs_text for w in ["oval", "elliptical", "waxy", "glossy", "curved shape"])

    # 2. Pathognomonic Lesion Clues
    has_rust = any(w in obs_text for w in ["rust", "orange", "cinnamon", "pustule", "pustules", "reddish-orange", "yellow or brown", "orange-yellow", "powdery pustule"])
    has_powdery = any(w in obs_text for w in ["powdery", "white powder", "talcum", "white mold", "white spots on it", "white substance"])
    has_bullseye = any(w in obs_text for w in ["concentric", "bullseye", "target", "rings"])
    has_water_soaked = any(w in obs_text for w in ["water-soaked", "greasy", "downy", "cottony"])
    has_bird_eye = any(w in obs_text for w in ["white center", "tan center", "gray center", "bird's eye", "purple ring", "small round", "small holes", "round spots"])
    has_brown_spots = any(w in obs_text for w in ["brown spot", "brown spots", "red spot", "angular", "spots on it", "discoloration"])
    has_shot_hole = any(w in obs_text for w in ["shot-hole", "shot hole", "holes", "dropped out", "ragged"])
    has_curl = any(w in obs_text for w in ["curl", "cupping", "puckering", "stunt", "mottle", "mosaic"])

    is_clean = (
        any(w in obs_text for w in ["healthy", "clean", "no spots", "good condition"])
        and pixel_stats.get("healthy_green_pct", 0) > 75
        and pixel_stats.get("brown_dried_pct", 0) < 6
        and pixel_stats.get("pale_yellow_pct", 0) < 6
    )

    # 3. Score every class in the comprehensive master database
    class_scores = []

    for class_id, info in PLANTVILLAGE_MASTER_DB.items():
        score = 0
        crop = info.get("crop", "").lower()
        disease = info.get("disease", "").lower()
        symptoms = (info.get("visual_symptoms", "") + " " + info.get("lesion_pattern", "")).lower()
        morphology = info.get("leaf_morphology", "").lower()
        color_sig = info.get("color_signature", "").lower()

        # 0. NEURAL EMBEDDING MODEL PRIORITY (archive.zip + PlantVillage Trained)
        if neural_class and class_id == neural_class:
            if not clean_crop_hint or clean_crop_hint.lower() in crop or any(w in crop for w in clean_crop_hint.lower().split()):
                score += 120 + int(neural_sim * 0.5)

        # A. EXPLICIT CROP FILTER (Highest Priority)
        if clean_crop_hint:
            ch = clean_crop_hint.lower()
            if ch in crop or any(w in crop for w in ch.split()):
                score += 150  # Decisive crop lock
            else:
                score -= 100  # Completely exclude other crops

        # B. Direct Crop Mentions in Vision / Farmer Notes (if no explicit hint given)
        else:
            if "strawberry" in obs_text and "strawberry" in crop:
                score += 60
            elif "coffee" in obs_text and "coffee" in crop:
                score += 60
            elif "soybean" in obs_text and "soybean" in crop:
                score += 60
            elif "rice" in obs_text and "rice" in crop:
                score += 60
            elif "wheat" in obs_text and "wheat" in crop:
                score += 60
            elif "cotton" in obs_text and "cotton" in crop:
                score += 60
            elif "banana" in obs_text and "banana" in crop:
                score += 60
            elif "mango" in obs_text and "mango" in crop:
                score += 60
            elif "corn" in obs_text or "maize" in obs_text:
                if "corn" in crop: score += 50
            elif "potato" in obs_text and "potato" in crop:
                score += 45
            elif "apple" in obs_text and "apple" in crop:
                score += 45
            elif "grape" in obs_text and "grape" in crop:
                score += 45
            elif "tomato" in obs_text and "tomato" in crop:
                score += 35  # Moderate, don't let tomato dominate

        # C. Leaf Morphology Matching
        if is_serrated:
            if "strawberry" in crop: score += 30
            elif "apple" in crop or "cherry" in crop or "peach" in crop: score += 15
        if is_lobed:
            if any(cr in crop for cr in ["grape", "squash", "cotton"]): score += 30
        if is_grassy:
            if any(cr in crop for cr in ["corn", "rice", "wheat", "sugarcane"]): score += 35
        if is_trifoliate:
            if any(cr in crop for cr in ["soybean", "strawberry"]): score += 30
        if is_oval_waxy:
            if any(cr in crop for cr in ["coffee", "orange", "citrus", "mango"]): score += 25

        # D. Specific Pathogen & Lesion Matching
        if has_rust:
            if "rust" in disease or "pustule" in symptoms: score += 40
            if "coffee" in crop: score += 30  # Coffee leaf rust priority
            if "wheat" in crop or "corn" in crop or "soybean" in crop: score += 20
        if has_bird_eye or (has_brown_spots and is_serrated):
            if "strawberry" in crop and ("spot" in disease or "scorch" in disease):
                score += 50
        if has_brown_spots or ("red spot" in obs_text):
            if "soybean" in crop and "brown spot" in disease:
                score += 45
            elif "coffee" in crop and "brown eye" in disease:
                score += 30
            elif "apple" in crop and "rot" in disease:
                score += 20
        if has_powdery and ("powdery" in disease or "mildew" in disease):
            score += 35
        if has_bullseye and ("early blight" in disease or "target" in disease):
            score += 40
        if has_water_soaked and ("late blight" in disease or "bacterial" in disease):
            score += 35
        if has_shot_hole and ("peach" in crop or "shot" in symptoms):
            score += 35
        if has_curl and ("curl" in disease or "mosaic" in disease):
            score += 35

        # E. Pixel Discoloration Correlation
        yellow_pct = pixel_stats.get("pale_yellow_pct", 0)
        brown_pct = pixel_stats.get("brown_dried_pct", 0)
        healthy_pct = pixel_stats.get("healthy_green_pct", 0)

        if is_clean and info["is_healthy"]:
            score += 50
        elif (yellow_pct + brown_pct > 12) and info["is_healthy"]:
            score -= 30  # Clearly diseased leaf, penalize healthy classes
        elif (yellow_pct + brown_pct > 20) and not info["is_healthy"]:
            score += 15  # Matches disease severity

        # F. Keyword Overlap
        for kw in ["spot", "brown", "yellow", "orange", "rust", "blight", "scab", "rot", "mold", "lesion"]:
            if kw in obs_text and (kw in symptoms or kw in color_sig):
                score += 2

        class_scores.append((score, class_id, info))

    class_scores.sort(key=lambda x: x[0], reverse=True)
    best_match = class_scores[0][2]
    top_candidates = [x[2] for x in class_scores[:5]]

    return {
        "best_match": best_match,
        "top_candidates": top_candidates,
        "scores": [(x[0], x[1]) for x in class_scores[:5]]
    }
