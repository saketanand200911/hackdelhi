"""
PlantVillage Master Agronomy Pathology Engine
Contains complete ground-truth disease definitions, leaf morphology,
lesion patterns, organic and chemical treatments, and local outbreak protocols
for all 38 classes in the PlantVillage Dataset (raw directory).
"""

from typing import Dict, Any, List, Optional

PLANTVILLAGE_MASTER_DB: Dict[str, Dict[str, Any]] = {
    # APPLE (4 classes)
    "Apple___Apple_scab": {
        "crop": "Apple",
        "disease": "Apple Scab (Venturia inaequalis)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Simple ovate leaves with serrated margins",
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
        "severity": "Severe",
        "organic_treatment": [
            "Prune and burn dead wood, fire blight cankers, and mummified hanging fruit",
            "Maintain optimal tree vigor and avoid mechanical trunk wounds"
        ],
        "chemical_treatment": [
            "Apply Thiophanate-methyl 70% WP or Captan 50% WP from petal fall through cover sprays"
        ],
        "outbreak_risk": "Moderate",
        "neighbor_alert": "Black rot canker spores detected. Inspect nearby apple and stone fruit trees for dead twig cankers.",
        "hindi_summary": "सेब में ब्लैक रॉट (मेंढक-आंख जैसे धब्बे) दिखा है। सूखी टहनियां काट कर अलग करें और कवकनाशी का छिड़काव करें।"
    },
    "Apple___Cedar_apple_rust": {
        "crop": "Apple",
        "disease": "Cedar Apple Rust (Gymnosporangium juniperi-virginianae)",
        "pathogen_type": "Fungal (Gymnosporangium)",
        "leaf_morphology": "Simple ovate leaves with serrated margins",
        "color_signature": "Bright yellow-orange to reddish-orange spots on upper leaf surface",
        "lesion_pattern": "Vibrant orange circular spots with small black pycnial specks in center",
        "is_healthy": False,
        "severity": "Moderate to High",
        "organic_treatment": [
            "Eradicate eastern red cedar and wild juniper trees within 1km of the orchard",
            "Spray sulfur or copper-based fungicide at pink bud stage"
        ],
        "chemical_treatment": [
            "Apply Myclobutanil 20% EW @ 0.5ml/L or Propiconazole 25% EC at 7-10 day intervals"
        ],
        "outbreak_risk": "High (wind carries basidiospores up to 2-3 km from alternate cedar hosts)",
        "neighbor_alert": "Cedar rust spores active in the area. Farmers with apple plots within 2km should inspect upper leaf foliage for bright orange spots.",
        "hindi_summary": "सेब की पत्ती पर चमकीले नारंगी जंग के धब्बे हैं। माइक्लोबुटानिल का छिड़काव करें और पास के देवदार/जूलिपर झाड़ियों को हटाएं।"
    },
    "Apple___healthy": {
        "crop": "Apple",
        "disease": "Healthy Apple Foliage",
        "pathogen_type": "None",
        "leaf_morphology": "Simple ovate serrated leaf",
        "color_signature": "Uniform deep green leaf blade, no discoloration",
        "lesion_pattern": "Smooth unblemished surface with prominent green venation",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": [
            "Apply balanced organic compost and maintain soil moisture with wood chip mulch",
            "Perform regular summer aeration pruning"
        ],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Plot is completely healthy. Continue routine preventive organic maintenance.",
        "hindi_summary": "सेब की पत्ती पूरी तरह स्वस्थ और हरी है। किसी रासायनिक छिड़काव की जरूरत नहीं है।"
    },

    # BLUEBERRY (1 class)
    "Blueberry___healthy": {
        "crop": "Blueberry",
        "disease": "Healthy Blueberry",
        "pathogen_type": "None",
        "leaf_morphology": "Small ovate-elliptic leaves with entire smooth margins",
        "color_signature": "Glossy vibrant emerald green",
        "lesion_pattern": "Clean glossy cuticle with no chlorosis or leaf spots",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": [
            "Maintain acidic soil pH (4.5 - 5.2) with peat moss and pine needle mulch",
            "Apply organic fish emulsion or balanced ammonium sulfate fertilizer"
        ],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "No disease present in this plot.",
        "hindi_summary": "ब्लूबेरी की पत्तियां पूरी तरह स्वस्थ हैं।"
    },

    # CHERRY (2 classes)
    "Cherry_(including_sour)___Powdery_mildew": {
        "crop": "Cherry",
        "disease": "Cherry Powdery Mildew (Podosphaera clandestina)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Elliptic-ovate leaves with double serrations",
        "color_signature": "White talcum-like powdery mycelial patches on green foliage",
        "lesion_pattern": "Circular white powdery spots spreading over lamina, causing upward leaf cupping",
        "is_healthy": False,
        "severity": "Moderate",
        "organic_treatment": [
            "Spray 0.5% neem oil emulsion or potassium bicarbonate (5g/L)",
            "Prune water sprouts and dense foliage to improve solar penetration and ventilation"
        ],
        "chemical_treatment": [
            "Apply Tebuconazole 25.9% EC or Myclobutanil 20% EW at first sign of white mycelium"
        ],
        "outbreak_risk": "High (wind-borne conidia multiply in warm dry conditions with humid nights)",
        "neighbor_alert": "Powdery mildew detected in cherry plot. Adjacent fruit growers should monitor terminal shoots for white powder coating.",
        "hindi_summary": "चेरी की पत्ती पर सफेद चूर्ण (पाउडरी मिल्ड्यू) जमा है। नीम का तेल या टेबुकोनाज़ोल का छिड़काव करें।"
    },
    "Cherry_(including_sour)___healthy": {
        "crop": "Cherry",
        "disease": "Healthy Cherry",
        "pathogen_type": "None",
        "leaf_morphology": "Elliptic-ovate leaves with clean double-serrated margins",
        "color_signature": "Deep green with clear venation",
        "lesion_pattern": "Smooth surface free of white mildew or shot-holes",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Maintain balanced irrigation and winter dormant spray."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "No disease detected.",
        "hindi_summary": "चेरी का पौधा स्वस्थ है।"
    },

    # CORN / MAIZE (4 classes)
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "crop": "Corn (Maize)",
        "disease": "Gray Leaf Spot (Cercospora zeae-maydis)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Long parallel-veined strap-like maize leaves",
        "color_signature": "Tan to grayish-brown rectangular lesions",
        "lesion_pattern": "Strictly rectangular spots parallel to and delimited by leaf veins",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Crop rotation with legumes (soybean, groundnut) for at least 1-2 seasons",
            "Incorporate crop residues deeply into soil after harvest"
        ],
        "chemical_treatment": [
            "Apply Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1ml/L at silking/tasseling"
        ],
        "outbreak_risk": "High (warm, humid, overcast conditions accelerate leaf blight)",
        "neighbor_alert": "Gray leaf spot confirmed in corn plot. Neighboring maize farmers within 1km should inspect lower canopy for rectangular tan lesions.",
        "hindi_summary": "मक्के की पत्ती पर नसों के बीच आयताकार भूरे धब्बे (ग्रे लीफ स्पॉट) हैं। कवकनाशी का छिड़काव करें।"
    },
    "Corn_(maize)___Common_rust_": {
        "crop": "Corn (Maize)",
        "disease": "Common Rust (Puccinia sorghi)",
        "pathogen_type": "Fungal (Rust)",
        "leaf_morphology": "Long parallel-veined strap-like maize leaves",
        "color_signature": "Golden-brown to cinnamon-brown powdery pustules",
        "lesion_pattern": "Raised oval blisters on both leaf surfaces that rupture and release rust powder",
        "is_healthy": False,
        "severity": "Moderate to High",
        "organic_treatment": [
            "Plant certified rust-resistant maize hybrids",
            "Avoid excessive late-season nitrogen applications"
        ],
        "chemical_treatment": [
            "Apply Mancozeb 75% WP @ 2.5g/L or Propiconazole 25% EC @ 1ml/L before tassel emergence"
        ],
        "outbreak_risk": "Critical (airborne rust spores travel tens of kilometers on seasonal wind currents)",
        "neighbor_alert": "Common rust spores actively dispersing on wind. All smallholder maize fields (<2ha) in 3km radius should check flag leaves.",
        "hindi_summary": "मक्के की पत्तियों पर भूरी-नारंगी जंग (रस्ट) की फफोलेदार फुंसियां हैं। मैनकोज़ेब या प्रोपिकोनाज़ोल का छिड़काव करें।"
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "crop": "Corn (Maize)",
        "disease": "Northern Corn Leaf Blight (Exserohilum turcicum)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Long parallel-veined strap-like maize leaves",
        "color_signature": "Grayish-green to tan elongated cigar-shaped lesions",
        "lesion_pattern": "Large (2.5 to 15 cm long) elliptical lesions with smooth tapering ends",
        "is_healthy": False,
        "severity": "Severe",
        "organic_treatment": [
            "Deep tillage of old corn stover to bury overwintering fungal spores",
            "Select resistant cultivars with Ht genes"
        ],
        "chemical_treatment": [
            "Apply Pyraclostrobin 20% WG or Azoxystrobin + Propiconazole strobilurin mix"
        ],
        "outbreak_risk": "High",
        "neighbor_alert": "Northern leaf blight lesions spreading. Inspect fields for large cigar-shaped tan lesions.",
        "hindi_summary": "मक्के की पत्ती पर बड़े सिगार के आकार के भूरे घाव हैं। तुरंत कवकनाशी स्प्रे करें।"
    },
    "Corn_(maize)___healthy": {
        "crop": "Corn (Maize)",
        "disease": "Healthy Corn Foliage",
        "pathogen_type": "None",
        "leaf_morphology": "Long strap-like leaves with parallel veins",
        "color_signature": "Rich deep emerald green",
        "lesion_pattern": "Continuous unbroken chlorophyll along leaf blade with sturdy midrib",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Maintain balanced NPK fertilization and adequate ear-filling irrigation."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Corn crop is healthy and vigorous.",
        "hindi_summary": "मक्के की फसल पूरी तरह हरी और स्वस्थ है।"
    },

    # GRAPE (4 classes)
    "Grape___Black_rot": {
        "crop": "Grape",
        "disease": "Grape Black Rot (Guignardia bidwellii)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Palmately 3-5 lobed leaves with coarse teeth",
        "color_signature": "Small reddish-brown circular spots with dark brown margins",
        "lesion_pattern": "Circular necrotic spots with tiny black pycnidia specks arranged in rings",
        "is_healthy": False,
        "severity": "Severe",
        "organic_treatment": [
            "Meticulous dormant cane pruning; eliminate mummified berry clusters from canopy",
            "Open vine canopy with shoot positioning to accelerate morning dew evaporation"
        ],
        "chemical_treatment": [
            "Apply Mancozeb 75% WP @ 2.5g/L or Myclobutanil 20% EW @ 0.5ml/L before bloom"
        ],
        "outbreak_risk": "High",
        "neighbor_alert": "Black rot fungal spores active. Neighboring vineyards should apply protective spray before rain.",
        "hindi_summary": "अंगूर की पत्ती पर लाल-भूरे गोल धब्बे (ब्लैक रॉट) हैं। संक्रमित हिस्से हटाएं और मैंकोजेब स्प्रे करें।"
    },
    "Grape___Esca_(Black_Measles)": {
        "crop": "Grape",
        "disease": "Esca / Black Measles (Phaeomoniella chlamydospora)",
        "pathogen_type": "Complex Fungal Pathogen",
        "leaf_morphology": "Palmately lobed grape leaves",
        "color_signature": "Interveinal yellow/brown necrosis producing a vivid 'tiger-stripe' pattern",
        "lesion_pattern": "Sharp bands of yellow chlorosis and brown necrosis alternating with green veins",
        "is_healthy": False,
        "severity": "Severe",
        "organic_treatment": [
            "Sanitize pruning shears with 70% alcohol between vines",
            "Protect large pruning wounds immediately with wound sealant paste"
        ],
        "chemical_treatment": ["No curative chemical exists; prune out affected cordons cleanly."],
        "outbreak_risk": "Moderate",
        "neighbor_alert": "Esca decline symptoms reported in grape vine. Sanitize all pruning tools to prevent vineyard spread.",
        "hindi_summary": "अंगूर में एस्का (बाघ की धारियों जैसे पीले-भूरे पत्ते) रोग है। छंटाई के औजार सैनिटाइज करें।"
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "crop": "Grape",
        "disease": "Grape Leaf Blight (Isariopsis cladosporioides)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Palmately lobed grape foliage",
        "color_signature": "Irregular dark brown to black necrotic blotches on older leaves",
        "lesion_pattern": "Angular brown spots with faint yellow halos coalescing into large scorched areas",
        "is_healthy": False,
        "severity": "Moderate",
        "organic_treatment": ["Prune lower canopy leaves to reduce ground moisture and increase airflow."],
        "chemical_treatment": ["Spray Copper Oxychloride 50% WP @ 2.5g/L or Difenoconazole 25% EC."],
        "outbreak_risk": "Moderate",
        "neighbor_alert": "Leaf blight active on older grape leaves. Ensure canopy airflow.",
        "hindi_summary": "अंगूर के पत्तों पर भूरा झुलसा रोग है। कॉपर ऑक्सीक्लोराइड का छिड़काव करें।"
    },
    "Grape___healthy": {
        "crop": "Grape",
        "disease": "Healthy Grape Vine",
        "pathogen_type": "None",
        "leaf_morphology": "Palmately lobed healthy grape foliage",
        "color_signature": "Bright supple green",
        "lesion_pattern": "Clean lamina, intact serrated lobes, no necrotic lesions",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Maintain balanced trellis pruning and consistent potassium nutrition."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Vineyard plot is healthy.",
        "hindi_summary": "अंगूर की बेल पूरी तरह स्वस्थ है।"
    },

    # ORANGE / CITRUS (1 class)
    "Orange___Haunglongbing_(Citrus_greening)": {
        "crop": "Orange / Citrus",
        "disease": "Citrus Greening / Huanglongbing (Candidatus Liberibacter asiaticus)",
        "pathogen_type": "Bacterial (Phloem-limited, Psyllid vector)",
        "leaf_morphology": "Elliptic-ovate leaves with winged petioles",
        "color_signature": "Asymmetric blotchy yellow mottle crossing leaf veins irregularly",
        "lesion_pattern": "Uneven yellowing on one side of midrib, corky raised veins, thickened leathery blade",
        "is_healthy": False,
        "severity": "Critical",
        "organic_treatment": [
            "Intensive Asian citrus psyllid suppression using neem oil (10,000 ppm) and horticultural oils",
            "Promptly uproot and destroy severely infected trees to protect surrounding grove"
        ],
        "chemical_treatment": [
            "Target psyllid vector with systemic Imidacloprid 17.8% SL or Thiamethoxam 25% WG"
        ],
        "outbreak_risk": "Critical (quarantine threat transmitted by citrus psyllids across orchards)",
        "neighbor_alert": "CRITICAL CITRUS ALERT: Citrus greening symptoms detected. All citrus orchards within 5km must inspect for yellow shoot mottle and control psyllid vectors immediately.",
        "hindi_summary": "संतरे/नींबू में सिट्रस ग्रीनिंग (पत्तियों का बेतरतीब पीलापन) है। तुरंत रसचूसक कीड़ों का नियंत्रण करें और गंभीर पौधों को नष्ट करें।"
    },

    # PEACH (2 classes)
    "Peach___Bacterial_spot": {
        "crop": "Peach",
        "disease": "Peach Bacterial Spot (Xanthomonas arboricola pv. pruni)",
        "pathogen_type": "Bacterial",
        "leaf_morphology": "Long lanceolate (sword-like) leaves with fine serrations",
        "color_signature": "Small angular dark purple to black water-soaked lesions",
        "lesion_pattern": "Center of lesions dries, cracks, and falls out, creating a distinct 'shot-hole' appearance",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Apply copper bactericide sprays during dormant and late bud break periods",
            "Plant windbreaks to prevent sandblasting and leaf wounding during storms"
        ],
        "chemical_treatment": [
            "Spray Copper Hydroxide at low rates or Oxytetracycline during growing season"
        ],
        "outbreak_risk": "High (wind-driven rain spreads bacteria rapidly)",
        "neighbor_alert": "Bacterial shot-hole active. Avoid overhead irrigation and spray preventive copper bactericide.",
        "hindi_summary": "आड़ू की पत्ती में छेददार बैक्टीरियल स्पॉट (शॉट-होल) रोग है। कॉपर दवा का छिड़काव करें।"
    },
    "Peach___healthy": {
        "crop": "Peach",
        "disease": "Healthy Peach Leaf",
        "pathogen_type": "None",
        "leaf_morphology": "Long lanceolate glossy leaves",
        "color_signature": "Vibrant emerald green, clean margin",
        "lesion_pattern": "Intact blade without holes or necrotic lesions",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Annual winter dormant spray and balanced compost."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Peach trees are healthy.",
        "hindi_summary": "आड़ू का पेड़ पूरी तरह स्वस्थ है।"
    },

    # PEPPER / CHILLI (2 classes)
    "Pepper,_bell___Bacterial_spot": {
        "crop": "Pepper (Bell / Chilli)",
        "disease": "Bacterial Leaf Spot (Xanthomonas campestris pv. vesicatoria)",
        "pathogen_type": "Bacterial",
        "leaf_morphology": "Simple ovate leaves with smooth (entire) margins and pointed tips",
        "color_signature": "Small water-soaked dark brown circular spots with bright yellow chlorotic halos",
        "lesion_pattern": "Dark brown necrotic lesions with prominent yellow haloes, causing premature leaf drop",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Use certified disease-free hot water treated seeds (50°C for 25 mins)",
            "Spray copper hydroxide + bio-fungicide (Bacillus subtilis); avoid overhead irrigation"
        ],
        "chemical_treatment": [
            "Apply Copper Oxychloride 50% WP @ 3.0g/L + Streptocycline (100 ppm) bactericide"
        ],
        "outbreak_risk": "High (spreads rapidly in warm, rainy, humid conditions)",
        "neighbor_alert": "Bacterial leaf spot detected in chilli/pepper plot. Neighboring farmers should spray protective copper bactericide and avoid working in wet fields.",
        "hindi_summary": "मिर्च/शिमला मिर्च की पत्ती पर पीले घेरे वाले काले-भूरे धब्बे (बैक्टीरियल स्पॉट) हैं। कॉपर ऑक्सीक्लोराइड और स्ट्रेप्टोसाइक्लिन का छिड़काव करें।"
    },
    "Pepper,_bell___healthy": {
        "crop": "Pepper (Bell / Chilli)",
        "disease": "Healthy Pepper Foliage",
        "pathogen_type": "None",
        "leaf_morphology": "Simple smooth ovate leaves",
        "color_signature": "Glossy uniform dark green",
        "lesion_pattern": "Firm smooth lamina with pointed apex, free of spots, curl, or aphids",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Maintain organic mulch, consistent drip watering, and balanced calcium."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Pepper crop is healthy and clean.",
        "hindi_summary": "मिर्च का पौधा स्वस्थ है।"
    },

    # POTATO (3 classes)
    "Potato___Early_blight": {
        "crop": "Potato",
        "disease": "Potato Early Blight (Alternaria solani)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Compound pinnate leaves with large ovate leaflets",
        "color_signature": "Dark brown to black circular lesions with yellow chlorotic margin",
        "lesion_pattern": "Classic concentric 'bullseye' target rings on older lower leaves",
        "is_healthy": False,
        "severity": "Moderate to High",
        "organic_treatment": [
            "Spray Neem oil (10,000 ppm) with soap emulsion; prune lower leaves near soil",
            "Ensure adequate potassium and avoid plant drought stress"
        ],
        "chemical_treatment": [
            "Apply Chlorothalonil 75% WP @ 2.0g/L or Mancozeb 75% WP @ 2.5g/L every 7-10 days"
        ],
        "outbreak_risk": "High (spores multiply in alternating wet and dry warm weather)",
        "neighbor_alert": "Early blight target spots detected in potato crop. Nearby potato and tomato growers should inspect lower foliage and apply protective fungicide.",
        "hindi_summary": "आलू के निचले पत्तों पर गोल छल्लेदार भूरे धब्बे (अगेती झुलसा) हैं। नीम का तेल या मैंकोजेब स्प्रे करें।"
    },
    "Potato___Late_blight": {
        "crop": "Potato",
        "disease": "Potato Late Blight (Phytophthora infestans)",
        "pathogen_type": "Oomycete (Fungal-like water mold)",
        "leaf_morphology": "Compound pinnate potato foliage",
        "color_signature": "Large, irregular water-soaked dark greenish-brown to black lesions",
        "lesion_pattern": "Rapidly expanding water-soaked greasy patches; white fluffy mold on leaf undersides in wet mornings",
        "is_healthy": False,
        "severity": "Critical",
        "organic_treatment": [
            "Apply Bordeaux mixture 1% preventatively; rogue out and bury initial infected plants immediately",
            "Ensure ridge drainage so water never pools in potato rows"
        ],
        "chemical_treatment": [
            "Apply Metalaxyl-M + Mancozeb (Ridomil Gold MZ) @ 2.5g/L or Dimethomorph 50% WP @ 1.5g/L immediately"
        ],
        "outbreak_risk": "Epidemic (can devastate smallholder potato fields within 48-72 hours in cool humid weather)",
        "neighbor_alert": "URGENT LATE BLIGHT EPIDEMIC WARNING: Highly infectious Phytophthora spores active. All potato and tomato plots in 3km must spray systemic fungicide immediately.",
        "hindi_summary": "आलू में पछेती झुलसा (लेट ब्लाइट) का गंभीर प्रकोप है। पत्तियों पर गीले काले धब्बे और सफेद फफूंद है। तुरंत रिडोमिल या कॉपर का छिड़काव करें।"
    },
    "Potato___healthy": {
        "crop": "Potato",
        "disease": "Healthy Potato Foliage",
        "pathogen_type": "None",
        "leaf_morphology": "Compound pinnate foliage with clean ovate leaflets",
        "color_signature": "Lush vibrant green",
        "lesion_pattern": "Clean healthy leaflets with vigorous upright growth, no lesions or curling",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Maintain proper earthing up, drip irrigation, and compost."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Potato field is healthy and disease-free.",
        "hindi_summary": "आलू की फसल पूरी तरह स्वस्थ है।"
    },

    # RASPBERRY (1 class)
    "Raspberry___healthy": {
        "crop": "Raspberry",
        "disease": "Healthy Raspberry",
        "pathogen_type": "None",
        "leaf_morphology": "Pinnately compound 3-5 serrated leaflets with silver-white undersides",
        "color_signature": "Vibrant dark green above, silvery pale green below",
        "lesion_pattern": "Crisp serrated margins, no necrotic spots or cane blight",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Prune out old floricanes after fruiting and maintain trellis airflow."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Raspberry canes are healthy.",
        "hindi_summary": "रास्पबेरी की पत्तियां स्वस्थ हैं।"
    },

    # SOYBEAN (1 class)
    "Soybean___healthy": {
        "crop": "Soybean",
        "disease": "Healthy Soybean (Minor Leaf Spot / Fungal Pustules if blemished)",
        "pathogen_type": "None (or Minor Fungal if spots present)",
        "leaf_morphology": "Trifoliate compound leaf (3 oval-broad leaflets with fine hairs)",
        "color_signature": "Lush deep green, soft pubescent texture",
        "lesion_pattern": "Clean trifoliate leaflets, prominent veins, no mosaic mottle",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": [
            "Inoculate seed with Bradyrhizobium japonicum at planting for natural nitrogen fixation",
            "Spray neem oil emulsion (5ml/L) if small minor fungal rust spots appear"
        ],
        "chemical_treatment": [
            "Apply Pyraclostrobin or Tebuconazole if Asian Soybean Rust or Brown Spot exceeds 5% threshold"
        ],
        "outbreak_risk": "Low",
        "neighbor_alert": "Soybean plot is generally healthy. Routine surveillance advised.",
        "hindi_summary": "सोयाबीन की फसल सामान्य और स्वस्थ है। पत्तों पर कोई गंभीर बीमारी नहीं है।"
    },

    # SQUASH / CUCURBITS (1 class)
    "Squash___Powdery_mildew": {
        "crop": "Squash / Cucurbits",
        "disease": "Squash Powdery Mildew (Podosphaera xanthii)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Large palmately lobed, rough bristly round leaves",
        "color_signature": "Brilliant white talcum powder-like patches across upper leaf blade",
        "lesion_pattern": "Circular white powdery fungal spots expanding over whole surface; underlying leaf turns yellow then brown and dies",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Spray 10% raw cow milk solution or potassium bicarbonate (5g/L) every 7 days",
            "Spray neem extract (10,000 ppm) with mild soap emulsion on upper and lower surfaces"
        ],
        "chemical_treatment": [
            "Apply Difenoconazole 25% EC @ 0.5ml/L or Azoxystrobin 23% SC @ 1ml/L"
        ],
        "outbreak_risk": "High (powdery mildew spreads rapidly in warm dry air with humid canopies)",
        "neighbor_alert": "Powdery mildew outbreak active in cucurbit/squash plots. Inspect pumpkin, cucumber, and squash leaves for white flour-like powder.",
        "hindi_summary": "कद्दू/लौकी/खीरा के पत्तों पर सफेद पाउडर (पाउडरी मिल्ड्यू) जमा है। नीम का तेल या दूध के घोल का छिड़काव करें।"
    },

    # STRAWBERRY (2 classes)
    "Strawberry___Leaf_scorch": {
        "crop": "Strawberry",
        "disease": "Strawberry Leaf Scorch / Common Leaf Spot (Diplocarpon earlianum / Mycosphaerella fragariae)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Trifoliate (3 leaflets) with distinct, coarse saw-tooth (serrated) dentate margins and radiating veins",
        "color_signature": "Numerous small circular purplish, dark red, or brown spots, often with white or tan necrotic centers",
        "lesion_pattern": "Distinct 'bird's eye' spots (1-5mm) scattered thickly across serrated leaf lamina; coalescing into scorched burnt edges",
        "is_healthy": False,
        "severity": "Moderate to High",
        "organic_treatment": [
            "Prune off and safely destroy old scorched, heavily spotted leaves after harvest",
            "Apply pine needle or clean straw mulch to keep leaves off wet soil",
            "Spray Copper Hydroxide or bio-fungicide (Bacillus amyloliquefaciens)"
        ],
        "chemical_treatment": [
            "Apply Captan 50% WP @ 2.5g/L or Thiophanate-methyl 70% WP @ 1.5g/L at early leaf emergence and pre-bloom",
            "Apply Azoxystrobin 23% SC if spot density exceeds 10 per leaf"
        ],
        "outbreak_risk": "High (spores splash from infected crown and soil during rain or overhead watering)",
        "neighbor_alert": "Strawberry leaf scorch / spot confirmed on serrated foliage. Neighboring strawberry growers should prune old foliage, avoid overhead watering, and apply protective fungicide.",
        "hindi_summary": "स्ट्रॉबेरी की दांतेदार पत्ती पर जामुनी-सफेद गोल धब्बे (लीफ स्कॉर्च / लीफ स्पॉट) हैं। पुरानी खराब पत्तियों को काटें और कैप्टान या कॉपर का छिड़काव करें।"
    },
    "Strawberry___healthy": {
        "crop": "Strawberry",
        "disease": "Healthy Strawberry",
        "pathogen_type": "None",
        "leaf_morphology": "Trifoliate leaves with deep sawtooth serrations",
        "color_signature": "Lush glossy dark green",
        "lesion_pattern": "Firm clean serrated leaflets, no purplish spots or scorched tips",
        "is_healthy": True,
        "severity": "Healthy",
        "organic_treatment": ["Maintain straw mulch, drip watering, and balanced bio-fertilizer."],
        "chemical_treatment": ["None required."],
        "outbreak_risk": "Low",
        "neighbor_alert": "Strawberry plot is healthy and vigorous.",
        "hindi_summary": "स्ट्रॉबेरी के पत्ते स्वस्थ और चमकदार हरे हैं।"
    },

    # TOMATO (10 classes)
    "Tomato___Bacterial_spot": {
        "crop": "Tomato",
        "disease": "Tomato Bacterial Spot (Xanthomonas spp.)",
        "pathogen_type": "Bacterial",
        "leaf_morphology": "Compound pinnate tomato leaves with lobed leaflets",
        "color_signature": "Small (1-3mm) circular water-soaked dark brown spots with a distinct yellow halo",
        "lesion_pattern": "Spots coalesce, causing ragged tear-like holes and yellowing of the leaflet",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Spray Copper Hydroxide + Bacillus subtilis bio-control",
            "Avoid working in or harvesting tomato plants when foliage is wet"
        ],
        "chemical_treatment": [
            "Apply Copper Oxychloride 50% WP (3.0g/L) + Streptocycline (100 ppm) bactericide"
        ],
        "outbreak_risk": "High (wind-driven rain spreads bacteria rapidly)",
        "neighbor_alert": "Bacterial spot reported in tomato field. Neighboring farmers should spray protective copper bactericide.",
        "hindi_summary": "टमाटर की पत्ती पर पीले घेरे वाले छोटे काले धब्बे (बैक्टीरियल स्पॉट) हैं। कॉपर और स्ट्रेप्टोसाइक्लिन का छिड़काव करें।"
    },
    "Tomato___Early_blight": {
        "crop": "Tomato",
        "disease": "Tomato Early Blight (Alternaria solani / linariae)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Compound pinnate tomato leaves with lobed leaflets",
        "color_signature": "Dark brown circular spots with concentric target-board rings surrounded by pale yellow halo",
        "lesion_pattern": "Concentric 'bullseye' rings on lowest older foliage; leaves turn chlorotic yellow and drop",
        "is_healthy": False,
        "severity": "Moderate to High",
        "organic_treatment": [
            "Prune lower 30cm of foliage from soil; apply clean mulch around stems",
            "Spray Neem oil extract (10,000 ppm) with mild soap emulsion in the evening"
        ],
        "chemical_treatment": [
            "Apply Mancozeb 75% WP @ 2.5g/L or Azoxystrobin + Difenoconazole @ 1ml/L every 10 days"
        ],
        "outbreak_risk": "High (spores splash from soil during rain and irrigation)",
        "neighbor_alert": "Early blight target spots detected in lower tomato canopy. Check lower leaves and apply mulch.",
        "hindi_summary": "टमाटर के निचले पत्तों पर गोल छल्लेदार भूरे धब्बे (अगेती झुलसा) हैं। नीचे के खराब पत्ते काटें और मैंकोजेब स्प्रे करें।"
    },
    "Tomato___Late_blight": {
        "crop": "Tomato",
        "disease": "Tomato Late Blight (Phytophthora infestans)",
        "pathogen_type": "Oomycete",
        "leaf_morphology": "Compound pinnate tomato foliage",
        "color_signature": "Large irregular water-soaked dark olive to grayish-black lesions",
        "lesion_pattern": "Rapidly expanding water-soaked greasy patches; white cottony mold under wet conditions",
        "is_healthy": False,
        "severity": "Critical",
        "organic_treatment": [
            "Rogue out and bag heavily infected tomato plants immediately",
            "Apply copper sulfate or Bordeaux mixture 1% preventatively"
        ],
        "chemical_treatment": [
            "Apply Dimethomorph 50% WP @ 1.5g/L or Metalaxyl-M (Ridomil MZ) @ 2.5g/L immediately"
        ],
        "outbreak_risk": "Critical (airborne sporangia travel 5-10 km on cool humid winds)",
        "neighbor_alert": "CRITICAL LATE BLIGHT EPIDEMIC WARNING: Highly infectious airborne spores active. All tomato and potato growers in 5km must spray systemic fungicide immediately.",
        "hindi_summary": "टमाटर में पछेती झुलसा (लेट ब्लाइट) है। पत्ते तेजी से गलकर काले हो रहे हैं। तुरंत रिडोमिल या कॉपर का छिड़काव करें।"
    },
    "Tomato___Leaf_Mold": {
        "crop": "Tomato",
        "disease": "Tomato Leaf Mold (Passalora fulva)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Compound pinnate tomato foliage",
        "color_signature": "Pale green or yellow blotches on upper leaf surface",
        "lesion_pattern": "Lower leaf surface develops velvety olive-green to brown fungal growth",
        "is_healthy": False,
        "severity": "Moderate",
        "organic_treatment": [
            "Improve greenhouse/polyhouse ventilation to keep relative humidity below 80%",
            "Increase plant spacing for maximum sunlight penetration"
        ],
        "chemical_treatment": ["Spray Copper Hydroxide or Chlorothalonil 75% WP @ 2.0g/L."],
        "outbreak_risk": "High in humid polyhouses",
        "neighbor_alert": "Leaf mold active in tomato canopy. Increase ventilation.",
        "hindi_summary": "टमाटर की पत्ती की ऊपरी सतह पर पीलापन और निचली सतह पर जैतूनी फफूंद (लीफ मोल्ड) है। हवा का बहाव बढ़ाएं।"
    },
    "Tomato___Septoria_leaf_spot": {
        "crop": "Tomato",
        "disease": "Tomato Septoria Leaf Spot (Septoria lycopersici)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Compound pinnate tomato leaves with lobed leaflets",
        "color_signature": "Numerous small circular spots (2-4mm) with pale grayish-white centers and dark brown margins",
        "lesion_pattern": "Distinct pale gray center with tiny black pinpoint speck pycnidia visible inside each spot",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Remove lower infected foliage and destroy; 3-year crop rotation",
            "Apply heavy organic mulch to prevent rain splashing spores from soil"
        ],
        "chemical_treatment": ["Apply Mancozeb 75% WP or Chlorothalonil 75% WP @ 2.0g/L every 7-10 days."],
        "outbreak_risk": "High",
        "neighbor_alert": "Septoria leaf spot active in lower tomato canopy. Prune infected leaves.",
        "hindi_summary": "टमाटर के पत्तों पर भूरे घेरे और सफेद केंद्र वाले छोटे-छोटे धब्बे (सेप्टोरिया) हैं। मैंकोजेब का छिड़काव करें।"
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "crop": "Tomato",
        "disease": "Tomato Spider Mites (Tetranychus urticae)",
        "pathogen_type": "Pest (Arachnid / Mite)",
        "leaf_morphology": "Compound pinnate tomato leaves",
        "color_signature": "Fine yellow stippling / speckled chlorotic dots across leaf blade",
        "lesion_pattern": "Silken webbing on leaf undersides; leaves turn yellow, bronzed, dry, and brittle",
        "is_healthy": False,
        "severity": "High",
        "organic_treatment": [
            "Spray potassium insecticidal soap or neem oil (10,000 ppm) with high pressure under leaves",
            "Release predatory mites (Phytoseiulus persimilis) in early infestation"
        ],
        "chemical_treatment": [
            "Apply Abamectin 1.9% EC @ 1ml/L or Spiromesifen 22.9% SC @ 1ml/L miticide"
        ],
        "outbreak_risk": "High in hot, dry, dusty conditions",
        "neighbor_alert": "Spider mite populations increasing in tomato plots. Check leaf undersides for fine webbing.",
        "hindi_summary": "टमाटर में लाल मकड़ी (माइट्स) का हमला है। पत्तों पर बारीक जाले और पीलापन है। अबामेक्टिन या नीम का तेल स्प्रे करें।"
    },
    "Tomato___Target_Spot": {
        "crop": "Tomato",
        "disease": "Tomato Target Spot (Corynespora cassiicola)",
        "pathogen_type": "Fungal",
        "leaf_morphology": "Compound pinnate tomato foliage",
        "color_signature": "Small pinpoint brown lesions expanding into circular spots with light brown centers",
        "lesion_pattern": "Concentric dark rings with pale brown centers, similar to early blight but on upper canopy",
        "is_healthy": False,
        "severity": "Moderate",
        "organic_treatment": ["Space plants widely for maximum aeration; avoid overhead wetting."],
        "chemical_treatment": ["Apply Famoxadone + Cymoxanil or Boscalid fungicide."],
        "outbreak_risk": "Moderate",
        "neighbor_alert": "Target spot detected in tomato plot. Improve airflow.",
        "hindi_summary": "टमाटर पर टारगेट स्पॉट के गोल भूरे धब्बे हैं। हवा का आवागमन सुधारें।"
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "crop": "Tomato",
        "disease": "Tomato Yellow Leaf Curl Virus (TYLCV)",
        "pathogen_type": "Viral (Begomovirus, Whitefly vector)",
        "leaf_morphology": "Compound tomato foliage, severely deformed",
        "color_signature": "Bright yellow chlorosis on leaf margins with stunted pale foliage",
        "lesion_pattern": "Severe upward rolling and cupping of leaf margins, puckered small leaves, bushy stunted growth",
        "is_healthy": False,
        "severity": "Critical",
        "organic_treatment": [
            "Install yellow sticky traps (20 per acre) to catch whitefly vectors",
            "Erect 50-mesh insect netting around seedlings and spray neem extract regularly"
        ],
        "chemical_treatment": [
            "Control whitefly vector Bemisia tabaci with Acetamiprid 20% SP @ 0.5g/L or Spirotetramat"
        ],
        "outbreak_risk": "Critical (whiteflies transmit virus within 15-30 minutes across entire village clusters)",
        "neighbor_alert": "VIRAL TYLCV ALERT: Whitefly-transmitted Leaf Curl Virus detected in tomato. Neighboring vegetable plots must spray whitefly controls immediately to prevent field destruction.",
        "hindi_summary": "टमाटर में लीफ कर्ल वायरस (पत्तियां ऊपर मुड़ना और पीलापन) है। सफेद मक्खी (व्हाइटफ्लाई) का तुरंत नियंत्रण करें।"
    },
    "Tomato___Tomato_mosaic_virus": {
        "crop": "Tomato",
        "disease": "Tomato Mosaic Virus (ToMV)",
        "pathogen_type": "Viral (Tobamovirus, Mechanical vector)",
        "leaf_morphology": "Compound pinnate tomato foliage",
        "color_signature": "Alternating light and dark green mosaic mottle",
        "lesion_pattern": "Blistering, distortion, puckering, and extreme 'shoestring' narrowing of leaflets",
        "is_healthy": False,
        "severity": "Severe",
        "organic_treatment": [
            "Disinfect hands and tools in 10% trisodium phosphate or whole milk before touching plants",
            "Uproot and bury infected plants immediately; do not smoke or handle tobacco near tomatoes"
        ],
        "chemical_treatment": ["No chemical cure exists; plant certified ToMV-resistant hybrid varieties."],
        "outbreak_risk": "High (mechanically spread on pruning tools, hands, and clothing)",
        "neighbor_alert": "Mosaic virus detected. Sanitize all farm pruning tools with milk or disinfectant to prevent mechanical spread.",
        "hindi_summary": "टमाटर में मोज़ेक वायरस (पत्तियों पर हरा-पीला चितकबरापन) है। संक्रमित पौधों को उखाड़कर नष्ट करें और औजार सैनिटाइज करें।"
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
    }
}


def diagnose_with_master_engine(
    vision_description: str,
    pixel_stats: Dict[str, Any],
    crop_hint: Optional[str] = "",
    farmer_notes: Optional[str] = ""
) -> Dict[str, Any]:
    """
    Precision Deterministic Agronomic Diagnostic Matcher.
    Uses leaf morphology, pathognomonic symptoms, and color signatures
    from the 38-class PlantVillage benchmark dataset.
    """
    obs_text = f"{vision_description} {crop_hint or ''} {farmer_notes or ''}".lower()
    
    # 1. Botanical Leaf Morphology Clues
    is_serrated = any(w in obs_text for w in ["serrated", "tooth", "teeth", "saw", "jagged", "dentate"])
    is_lobed = any(w in obs_text for w in ["lobe", "lobed", "palmate", "webbed"])
    is_grassy = any(w in obs_text for w in ["grass", "corn", "narrow", "parallel", "maize", "strap"])
    is_trifoliate = any(w in obs_text for w in ["trifoliate", "three", "3 leaf"])
    
    # 2. Pathognomonic Lesion Clues
    has_rust = any(w in obs_text for w in ["rust", "orange", "cinnamon", "pustule", "reddish-orange"])
    has_powdery = any(w in obs_text for w in ["powdery", "white powder", "talcum", "mycelium", "white spots on it", "white substance"])
    has_bullseye = any(w in obs_text for w in ["concentric", "bullseye", "target", "rings"])
    has_water_soaked = any(w in obs_text for w in ["water-soaked", "greasy", "downy", "cottony"])
    has_scorch_spots = any(w in obs_text for w in ["small circular", "purple", "purplish", "spots with white", "spots with tan", "bird's eye", "scorch", "numerous", "many spots", "brown spots on it", "white spots on it"])
    has_shot_hole = any(w in obs_text for w in ["shot-hole", "shot hole", "holes", "dropped out"])
    has_curl = any(w in obs_text for w in ["curl", "cupping", "puckering", "stunt", "mottle", "mosaic"])
    is_clean = any(w in obs_text for w in ["healthy", "clean", "no spots", "good condition"]) and pixel_stats.get("healthy_green_pct", 0) > 75 and pixel_stats.get("brown_dried_pct", 0) < 6

    # Score each of the 38 PlantVillage classes
    class_scores = []
    
    for class_id, info in PLANTVILLAGE_MASTER_DB.items():
        score = 0
        crop = info.get("crop", "").lower()
        disease = info.get("disease", "").lower()
        symptoms = (info.get("visual_symptoms", "") + " " + info.get("lesion_pattern", "")).lower()
        morphology = info.get("leaf_morphology", "").lower()
        color_sig = info.get("color_signature", "").lower()
        
        # A. USER CROP HINT: Absolute Priority (60 pts)
        if crop_hint:
            ch = crop_hint.lower()
            if ch in crop or any(w in crop for w in ch.split()):
                score += 80
            else:
                score -= 40 # Penalize non-matching crops
                
        # B. Direct Crop Name Detected in Vision
        if not crop_hint:
            if "strawberry" in obs_text and "strawberry" in crop:
                score += 45
            elif "tomato" in obs_text and "tomato" in crop:
                score += 40
            elif "corn" in obs_text or "maize" in obs_text:
                if "corn" in crop: score += 40
            elif "potato" in obs_text and "potato" in crop:
                score += 40
            elif "apple" in obs_text and "apple" in crop:
                score += 40
            elif "grape" in obs_text and "grape" in crop:
                score += 40
            elif "pepper" in obs_text or "chilli" in obs_text:
                if "pepper" in crop: score += 40
            elif "soybean" in obs_text and "soybean" in crop:
                score += 40
            elif "squash" in obs_text or "cucumber" in obs_text or "cucurbit" in obs_text:
                if "squash" in crop: score += 40

        # C. Leaf Morphology Matching
        if is_serrated and any(cr in crop for cr in ["strawberry", "apple", "cherry"]):
            score += 20
        if is_serrated and any(w in obs_text for w in ["spot", "spots", "dot", "dots", "speck"]):
            if "strawberry" in crop and "scorch" in disease:
                score += 25
            elif "apple" in crop and "rot" in disease:
                score += 10
        if is_lobed and any(cr in crop for cr in ["grape", "squash"]):
            score += 20
        if is_grassy and "corn" in crop:
            score += 25
        if is_trifoliate and any(cr in crop for cr in ["strawberry", "soybean"]):
            score += 15

        # D. Specific Pathogen & Lesion Matching
        if has_rust and ("rust" in disease or "pustule" in symptoms):
            score += 25
        if has_powdery and ("powdery" in disease or "mildew" in disease):
            score += 25
        if has_bullseye and ("early blight" in disease or "target" in disease):
            score += 25
        if has_water_soaked and "late blight" in disease:
            score += 25
        if has_scorch_spots and "strawberry" in crop and "scorch" in disease:
            score += 30
        if has_shot_hole and "peach" in crop and "bacterial" in disease:
            score += 25
        if has_curl and ("curl" in disease or "mosaic" in disease):
            score += 25

        # E. Healthy vs Diseased Discrimination
        if is_clean and info["is_healthy"]:
            score += 35
        elif not is_clean and info["is_healthy"]:
            score -= 15

        # F. Keyword Overlap
        for kw in ["spot", "brown", "yellow", "blight", "scab", "rot", "mold", "lesion"]:
            if kw in obs_text and (kw in symptoms or kw in color_sig):
                score += 3

        class_scores.append((score, class_id, info))

    class_scores.sort(key=lambda x: x[0], reverse=True)
    best_match = class_scores[0][2]
    top_candidates = [x[2] for x in class_scores[:5]]

    return {
        "best_match": best_match,
        "top_candidates": top_candidates,
        "scores": [(x[0], x[1]) for x in class_scores[:5]]
    }
