"""Menus des 21 jours (déjeuner + dîner, 8 personnes) construits sur l'inventaire réel.

Entrée  : inventaire.json (ticket Pepito 28/10 + marché 29/10 + riz du bord)
Sortie  : menus-21j.json (repas injectés dans l'outil), menus-21j.md (lecture)
Contrôles :
  - chaque ingrédient existe dans l'inventaire (même nom, même unité) ;
  - les denrées qui se gardent ne dépassent pas ~70 % du stock (21 j sur 30 j de vivres) ;
  - les produits frais sont consommés avant leur limite de conservation estimée.
Hors repas (non comptés ici) : petits-déjeuners, collations, fruits, boissons.
"""
import json, sys
from collections import defaultdict
from pathlib import Path

ICI = Path(__file__).parent
inv = {i["name"]: i for i in json.load(open(ICI / "inventaire.json", encoding="utf-8"))}

H = "HUILE"  # huile de cuisson générique, répartie ensuite entre tournesol puis olive

# (jour, "dej"|"din", recette, {denrée: quantité}, préparation)
M = [
(1, "dej", "Salade de pâtes au thon, maïs grillé et concombre",
 {"Pâtes": 1.0, "Thon": 3, "Maïs (épis)": 6, "Concombres": 1.0, "Tomates fraîches": 0.5, "Oignons": 0.1,
  "Huile d'olive vierge extra": 0.06, "Moutarde forte": 0.1},
 "Cuire les pâtes al dente (moitié eau de mer, moitié eau douce), égoutter et refroidir. Griller les épis à sec dans une poêle 8 à 10 min en les tournant, puis les égrener. Couper concombre et tomates en dés, émincer finement l'oignon. Vinaigrette : huile d'olive, 1 c. à s. de moutarde, sel, poivre. Mélanger le tout avec le thon égoutté."),
(1, "din", "Curry de poulet coco et pommes de terre, riz",
 {"Blanc de poulet": 0.9, "Lait de coco": 2, "Pommes de terre": 1.2, "Tomates fraîches": 0.4, "Oignons": 0.25, "Ail": 0.03,
  "Gingembre": 0.05, "Curry de Madras en poudre": 0.1, H: 0.05, "Riz": 0.4},
 "Lancer le riz au multicuiseur. Faire revenir oignons, ail et gingembre hachés 5 min, ajouter 3 c. à s. de curry et laisser 1 min. Ajouter le poulet en cubes et le dorer 5 min, puis les pommes de terre en dés, les tomates et le lait de coco. Couvrir et mijoter 20 min, jusqu'à ce que les pommes de terre soient tendres. Saler."),
(2, "dej", "Poke bowl de thon, quinoa, concombre et haricots longs",
 {"Filets de poisson": 1.0, "Quinoa blanc": 2, "Concombres": 1.0, "Haricots longs": 1, "Graines de sésame": 0.05,
  "Citrons verts": 3, "Gingembre": 0.03, "Sauce sweet chili (Flying Goose)": 0.15, "Huile d'olive vierge extra": 0.03},
 "Décongeler le thon au frigo la veille. Rincer le quinoa, le cuire 15 min dans 2 volumes d'eau, laisser refroidir. Couper le thon en cubes de 2 cm et le mariner 10 min dans le jus des citrons, le gingembre râpé, l'huile et 2 c. à s. de sauce sweet chili. S'il n'a pas été congelé dès l'achat, le saisir 30 s par face. Blanchir les haricots longs coupés 3 min, rafraîchir. Dresser en bols avec le concombre en dés et le sésame grillé à sec."),
(2, "din", "Tofu soyeux sambal, haricots longs sautés et riz",
 {"Tofu soyeux": 5, "Haricots longs": 2, "Sambal": 0.03, "Sauce Bangkok (Kokita)": 0.15, "Oignons": 0.15, "Ail": 0.03,
  "Gingembre": 0.03, H: 0.05, "Riz": 0.6},
 "Lancer le riz. Faire revenir oignon, ail et gingembre, ajouter 2 c. à s. de sambal, la sauce Bangkok et un verre d'eau. Glisser le tofu en gros cubes et laisser chauffer 5 min sans remuer : il est fragile, l'arroser de sauce à la cuillère. À côté, sauter les haricots longs coupés 5 min à feu vif avec un peu d'ail."),
(3, "dej", "Rouleaux de printemps, omelette et crudités, sauce cacahuète",
 {"Galettes de riz (feuilles)": 1, "Nouilles de riz": 1, "Œufs": 8, "Concombres": 1.0, "Carottes": 0.3, "Chou blanc": 0.25,
  "Beurre cacahuète-amande": 0.5, "Citrons verts": 1, "Sauce sweet chili (Flying Goose)": 0.1, H: 0.02},
 "Tremper les nouilles de riz 10 min dans l'eau chaude, égoutter. Faire une omelette fine avec les 8 œufs et la couper en lanières. Couper concombre, carotte et chou en fine julienne. Sauce au mixeur : beurre cacahuète-amande, jus du citron, sweet chili et un peu d'eau chaude. Chacun roule ses galettes après les avoir trempées 5 s dans l'eau tiède."),
(3, "din", "Haricots rouges mijotés tomate-sambal, maïs et cheddar, riz",
 {"Haricots rouges secs": 1.2, "Tomates concassées": 1.5, "Maïs (épis)": 6, "Oignons": 0.25, "Ail": 0.04, "Sambal": 0.02,
  "Curry de Madras en poudre": 0.05, "Cheddar": 0.15, H: 0.04, "Riz": 0.3},
 "La veille au soir (J2), tremper 2 kg de haricots rouges : 1,2 kg pour ce soir, 0,8 kg pour demain midi. Les égoutter, couvrir d'eau neuve, bouillir 10 min à gros bouillons (indispensable pour les haricots rouges), puis cuire 1 h à 1 h 30 jusqu'à ce qu'ils soient tendres. Réserver la part de demain. Faire revenir oignons et ail, ajouter curry, sambal, tomates, maïs égrené et les haricots, mijoter 20 min. Servir avec le riz et le cheddar râpé."),
(4, "dej", "Bol burrito : haricots rouges, riz, salsa concombre-tomate, yaourt citronné",
 {"Haricots rouges secs": 0.8, "Riz": 0.3, "Concombres": 1.0, "Tomates fraîches": 0.6, "Maïs (épis)": 4, "Yaourt nature": 0.5,
  "Citrons verts": 1, "Oignons": 0.1, "Cheddar": 0.1, "Sambal": 0.01},
 "Réchauffer les haricots cuits hier avec un peu d'eau. Cuire le riz. Griller les épis et les égrener. Salsa : concombre, tomate et oignon en petits dés, la moitié du citron, sel. Sauce : yaourt, reste du citron, sel. Monter les bols et parsemer de cheddar râpé."),
(4, "din", "Soupe au tofu soyeux, vermicelles et citronnelle, œufs pochés",
 {"Tofu soyeux": 5, "Vermicelles de soja (Longkou)": 1, "Haricots longs": 2, "Carottes": 0.2, "Chou blanc": 0.25,
  "Citronnelle": 2, "Gingembre": 0.06, "Ail": 0.03, "Œufs": 8, "Sambal": 0.02, "Riz": 0.4},
 "Bouillon : 4 L d'eau, citronnelle écrasée, gingembre en lamelles et ail, 15 min à frémissement (ajouter un cube ou de la sauce soja si vous en avez, sinon saler). Ajouter carottes et chou émincés 5 min, les haricots longs 3 min, puis les vermicelles trempés. Pocher les œufs 3 min dans le bouillon frémissant et glisser le tofu en cubes à la fin. Riz à part, sambal à table."),
(5, "dej", "Salade de haricots blancs, thon, concombre et tomate",
 {"Haricots blancs secs": 0.8, "Thon": 3, "Concombres": 1.0, "Tomates fraîches": 0.5, "Oignons": 0.1,
  "Citrons verts": 2, "Huile d'olive vierge extra": 0.06, "Herbes italiennes": 0.2, "Moutarde forte": 0.1},
 "Tremper les haricots blancs la veille au soir. Le matin, les cuire 1 h à 1 h 15 dans de l'eau non salée, saler en fin de cuisson et laisser refroidir. Les mélanger avec le thon, le concombre et la tomate en dés et l'oignon émincé. Vinaigrette : citron, huile, moutarde, herbes, sel, poivre."),
(5, "din", "Pizzas à la poêle (pâte au yaourt), tomate, mozzarella, olives et maïs",
 {"Farine de blé": 1.0, "Yaourt nature": 0.6, "Mozzarella râpée": 0.5, "Tomates concassées": 1.5, "Olives noires": 1,
  "Câpres": 0.25, "Maïs (épis)": 4, "Oignons": 0.15, "Herbes italiennes": 0.2, "Huile d'olive vierge extra": 0.05},
 "Pâte : 1 kg de farine, 600 ml de yaourt, 1 c. à c. de sel, un peu d'eau si besoin ; pétrir 5 min et laisser reposer 20 min. Sauce : tomates, oignon et herbes réduits 10 min. Diviser la pâte en 8 et l'étaler finement. Cuire dans une poêle huilée, couvercle fermé, 3 min à feu moyen, retourner, garnir (sauce, mozzarella, olives, câpres, maïs grillé égrené) et couvrir 4 à 5 min jusqu'à ce que le fromage fonde. Sans four, c'est le couvercle qui fait le travail."),
(6, "dej", "Tortilla de pommes de terre et oignons, salade de chou-carotte",
 {"Œufs": 12, "Pommes de terre": 1.5, "Oignons": 0.3, H: 0.08, "Chou blanc": 0.25, "Carottes": 0.2, "Moutarde forte": 0.1},
 "Couper les pommes de terre en fines lamelles et émincer les oignons ; les cuire doucement 20 min à couvert dans l'huile en remuant. Battre les 12 œufs avec du sel, ajouter les pommes de terre égouttées. Cuire en 2 poêles 8 min à feu doux et couvert, retourner sur une assiette, puis 3 min de l'autre côté. Salade : chou et carotte râpés, moutarde, un filet d'huile."),
(6, "din", "Curry de tofu soyeux et patate douce au lait de coco, riz",
 {"Tofu soyeux": 5, "Patates douces": 1.2, "Lait de coco": 2, "Curry de Madras en poudre": 0.1, "Citronnelle": 1,
  "Gingembre": 0.05, "Ail": 0.03, "Oignons": 0.15, H: 0.04, "Riz": 0.4},
 "Riz. Faire revenir oignon, ail, gingembre et citronnelle écrasée, ajouter 3 c. à s. de curry. Ajouter la patate douce en cubes de 2 cm, le lait de coco et un verre d'eau, mijoter 15 min. Glisser le tofu en cubes et laisser 5 min sans remuer. C'est le dernier tofu : ne pas le garder au-delà de ce jour."),
(7, "dej", "Nouilles de riz sautées au poulet façon pad thaï, cajou",
 {"Nouilles de riz": 2, "Blanc de poulet": 0.9, "Œufs": 8, "Chou blanc": 0.25, "Carottes": 0.2, "Noix de cajou grillées": 0.12,
  "Sauce Bangkok (Kokita)": 0.15, "Sambal": 0.02, "Ail": 0.03, "Oignons": 0.1, H: 0.06},
 "Tremper les nouilles 10 min dans l'eau chaude. Saisir le poulet en lanières à feu vif, réserver. Brouiller les œufs, réserver. Faire sauter ail, oignon, chou et carotte 3 min, ajouter les nouilles égouttées, la sauce Bangkok, le sambal et un peu d'eau, remuer 2 min. Remettre poulet et œufs. Parsemer de cajou concassés."),
(7, "din", "Dahl de lentilles au lait de coco, chapatis",
 {"Lentilles en conserve": 3, "Lait de coco": 1.5, "Tomates pelées": 1, "Oignons": 0.25, "Ail": 0.03, "Gingembre": 0.05,
  "Mélange d'épices indien": 0.25, "Graines de moutarde noire": 0.2, "Farine de blé": 0.75, "Margarine": 0.05, H: 0.04},
 "Chapatis : 750 g de farine, environ 450 ml d'eau tiède et du sel ; pétrir, laisser reposer 20 min, faire 16 boules, les étaler et les cuire à sec 1 min par face ; badigeonner de margarine. Dahl : chauffer l'huile, y jeter les graines de moutarde jusqu'à ce qu'elles sautent, ajouter oignon, ail et gingembre, puis les épices 1 min. Ajouter les tomates, les lentilles égouttées et le lait de coco, mijoter 15 min et écraser un peu."),
(8, "dej", "Riz aux haricots rouges, guacamole et chou croquant",
 {"Haricots rouges secs": 1.3, "Riz": 0.5, "Avocats": 1.5, "Citrons verts": 2, "Oignons": 0.1, "Chou blanc": 0.25,
  "Sambal": 0.02, "Ail": 0.02},
 "Tremper les haricots la veille au soir, puis les cuire le matin (10 min à gros bouillons, puis 1 h à 1 h 30). Mélanger les haricots chauds avec le riz cuit, l'ail et le sel. Guacamole : avocats écrasés, citron, oignon haché fin, sambal, sel. Servir avec le chou émincé finement."),
(8, "din", "Poulet sauté citronnelle-gingembre et chayote, riz",
 {"Blanc de poulet": 0.9, "Chayote": 1.0, "Citronnelle": 2, "Gingembre": 0.08, "Ail": 0.03, "Oignons": 0.15,
  "Sauce Bangkok (Kokita)": 0.1, H: 0.05, "Riz": 0.6},
 "Riz. Hacher finement la citronnelle (le cœur tendre), le gingembre et l'ail. Saisir le poulet en lanières à feu vif 4 min, réserver. Faire sauter la chayote épluchée en bâtonnets avec l'oignon 5 min, ajouter le hachis et le poulet, la sauce Bangkok et un trait d'eau, 2 min."),
(9, "dej", "Pâtes aux sardines, tomate, câpres et olives vertes",
 {"Pâtes": 1.0, "Sardines (grande boîte)": 3, "Tomates concassées": 1.5, "Câpres": 0.25, "Olives vertes dénoyautées": 1,
  "Ail": 0.03, "Oignons": 0.1, "Huile d'olive vierge extra": 0.04, "Parmesan râpé": 0.1},
 "Cuire les pâtes. Faire revenir ail et oignon dans l'huile, ajouter les tomates et laisser réduire 10 min. Ajouter les sardines en morceaux, les câpres et les olives coupées, 3 min. Mélanger avec les pâtes et servir avec le parmesan."),
(9, "din", "Thon poêlé, purée de patate douce et chou sauté au gingembre",
 {"Filets de poisson": 1.0, "Patates douces": 1.5, "Margarine": 0.08, "Chou blanc": 0.5, "Gingembre": 0.03, "Ail": 0.02, H: 0.04},
 "Décongeler le thon au frigo la veille. Cuire les patates douces à la vapeur (multicuiseur) 20 min, les écraser avec la margarine et du sel. Couper le thon en pavés de 2 cm d'épaisseur, saler, saisir 1 à 2 min par face à feu très vif. Faire sauter le chou émincé avec le gingembre et l'ail 4 min."),
(10, "dej", "Salade de quinoa rouge, pois chiches, avocat et carotte",
 {"Quinoa rouge": 2, "Pois chiches": 3, "Avocats": 1.5, "Carottes": 0.1, "Oignons": 0.1, "Citrons verts": 2,
  "Huile d'olive vierge extra": 0.06, "Graines de sésame": 0.05},
 "Rincer le quinoa et le cuire 15 min dans 2 volumes d'eau, laisser refroidir. Ajouter les pois chiches rincés, la carotte râpée, l'oignon émincé et l'avocat en dés. Assaisonner avec citron, huile, sel et sésame grillé à sec."),
(10, "din", "Curry de soja et courge au lait de coco, riz",
 {"Graines de soja sèches": 1.1, "Courge": 0.5, "Lait de coco": 2, "Curry de Madras en poudre": 0.1, "Gingembre": 0.05,
  "Ail": 0.03, "Oignons": 0.2, H: 0.04, "Riz": 0.4},
 "Le soja est long : le tremper 12 h la veille (2 kg : 1,1 kg pour ce soir, 0,9 kg pour les galettes de demain midi), puis le cuire 2 h 30 à 3 h jusqu'à ce qu'il soit tendre, idéalement dès le matin. Faire revenir oignon, ail et gingembre, ajouter le curry, la courge en cubes, le lait de coco et un verre d'eau, 15 min. Ajouter 1,1 kg (poids sec) de soja cuit, 10 min. Servir avec le riz."),
(11, "dej", "Galettes de soja aux oignons, sauce yaourt, quinoa",
 {"Graines de soja sèches": 0.9, "Œufs": 4, "Farine de blé": 0.1, "Oignons": 0.15, "Ail": 0.03, "Gingembre": 0.03,
  "Yaourt nature": 0.4, "Quinoa rouge": 1, H: 0.1},
 "Mixer grossièrement le soja cuit hier avec oignon, ail, gingembre, les œufs, la farine et du sel. Former 24 galettes et les dorer 3 min par face à la poêle huilée. Sauce : yaourt et sel. Cuire le quinoa 15 min dans 2 volumes d'eau et servir avec."),
(11, "din", "Minestrone de haricots blancs, courge et pommes de terre, parmesan",
 {"Haricots blancs secs": 0.8, "Courge": 0.5, "Pommes de terre": 1.0, "Chou blanc": 0.25, "Tomates pelées": 1, "Oignons": 0.2,
  "Ail": 0.03, "Herbes italiennes": 0.2, "Parmesan râpé": 0.1, "Huile d'olive vierge extra": 0.05},
 "Tremper les haricots la veille et les cuire 1 h le matin. Faire revenir oignon et ail dans l'huile, ajouter courge et pommes de terre en dés, les tomates, les herbes et 4 L d'eau, 20 min. Ajouter le chou et les haricots cuits, 10 min. Saler, servir avec le parmesan."),
(12, "dej", "Pizzas à la poêle au thon, oignon et olives",
 {"Farine de blé": 1.0, "Yaourt nature": 0.6, "Mozzarella râpée": 0.5, "Tomates concassées": 1.5, "Thon": 1.5,
  "Olives noires": 0.5, "Oignons": 0.15, "Herbes italiennes": 0.2, "Huile d'olive vierge extra": 0.05},
 "Même méthode que les pizzas du J5 : pâte farine-yaourt reposée 20 min, sauce tomate réduite aux herbes, cuisson à la poêle couverte 3 min, retourner, garnir de sauce, thon émietté, oignon, olives et mozzarella, couvrir 4 à 5 min. Ouvrir le second sachet de mozzarella aujourd'hui."),
(12, "din", "Maquereau à la tomate, gingembre et chayote, riz",
 {"Maquereau": 3, "Tomates pelées": 1, "Chayote": 1.0, "Gingembre": 0.05, "Ail": 0.03, "Oignons": 0.15, "Sambal": 0.02,
  H: 0.04, "Riz": 0.5},
 "Riz. Faire revenir oignon, ail et gingembre, ajouter la chayote en dés 5 min, puis les tomates et le sambal, 10 min. Ajouter le maquereau en gros morceaux avec un peu de son jus et réchauffer 3 min sans trop remuer."),
(13, "dej", "Nouilles de riz sautées au tempeh, chou et cajou",
 {"Nouilles de riz": 2, "Tempeh": 0.7, "Chou blanc": 0.25, "Oignons": 0.1, "Ail": 0.03, "Sauce Bangkok (Kokita)": 0.1,
  "Sambal": 0.02, "Noix de cajou grillées": 0.1, H: 0.06},
 "Décongeler le tempeh la veille. Le couper en bâtonnets et le dorer 6 à 8 min à la poêle. Tremper les nouilles 10 min. Faire sauter ail, oignon et chou 3 min, ajouter nouilles, sauce Bangkok, sambal et un trait d'eau, puis le tempeh et les cajou."),
(13, "din", "Haricots rouges façon rendang (coco, citronnelle, coco grillée), riz",
 {"Haricots rouges secs": 1.2, "Lait de coco": 2, "Citronnelle": 1, "Gingembre": 0.06, "Ail": 0.04, "Oignons": 0.2,
  "Sambal": 0.02, "Copeaux de coco séchés": 0.5, "Curry de Madras en poudre": 0.05, H: 0.04, "Riz": 0.5},
 "Tremper les haricots la veille, les cuire le matin (10 min à gros bouillons, puis 1 h à 1 h 30). Mixer oignon, ail, gingembre, citronnelle et sambal en pâte, la faire revenir 5 min avec le curry. Ajouter le lait de coco et les haricots, mijoter à découvert 25 min jusqu'à ce que la sauce épaississe. Griller les copeaux de coco à sec et les parsemer dessus."),
(14, "dej", "Salade de pommes de terre, maquereau et œufs durs à la moutarde",
 {"Pommes de terre": 1.5, "Maquereau": 3, "Œufs": 8, "Oignons": 0.1, "Moutarde forte": 0.2, "Huile d'olive vierge extra": 0.05},
 "Cuire les pommes de terre en robe 20 min à la vapeur, les couper en morceaux tièdes. Cuire les œufs 10 min. Vinaigrette : moutarde, huile, sel, poivre. Mélanger pommes de terre, maquereau émietté, œufs en quartiers et oignon émincé."),
(14, "din", "Poulet à l'ail, aux herbes et aux câpres, quinoa et chayote poêlée",
 {"Blanc de poulet": 0.9, "Quinoa blanc": 2, "Ail": 0.04, "Herbes italiennes": 0.2, "Câpres": 0.2, "Chayote": 1.0,
  "Huile d'olive vierge extra": 0.06},
 "Cuire le quinoa 15 min. Couper le poulet en aiguillettes, le saisir dans l'huile avec l'ail haché et les herbes 6 à 8 min, ajouter les câpres et un trait d'eau pour déglacer. Faire poêler la chayote épluchée en fines tranches 6 min."),
(15, "dej", "Houmous maison, œufs durs, chapatis et crudités",
 {"Pois chiches": 3, "Graines de sésame": 0.1, "Citrons verts": 2, "Ail": 0.02, "Huile d'olive vierge extra": 0.08,
  "Farine de blé": 0.75, "Œufs": 8, "Chou blanc": 0.25},
 "Griller le sésame à sec et le mixer avec un peu d'huile en pâte (tahini). Mixer les pois chiches égouttés avec ce tahini, l'ail, le citron, l'huile, du sel et un peu d'eau jusqu'à ce que ce soit lisse. Chapatis comme au J7 (750 g de farine). Cuire les œufs 10 min. Servir avec le chou en lanières."),
(15, "din", "Curry de thon et patate douce au lait de coco, riz",
 {"Filets de poisson": 1.0, "Patates douces": 1.5, "Lait de coco": 1.5, "Curry de Madras en poudre": 0.1, "Gingembre": 0.05,
  "Ail": 0.03, "Oignons": 0.15, H: 0.04, "Riz": 0.5},
 "Décongeler le thon au frigo la veille. Riz. Faire revenir oignon, ail, gingembre et curry, ajouter la patate douce en cubes, le lait de coco et un verre d'eau, 15 min. Ajouter le thon en gros cubes et cuire 4 min à frémissement, sans remuer pour qu'il reste moelleux."),
(16, "dej", "Ragoût de soja, patate douce et tomate aux épices indiennes, riz",
 {"Graines de soja sèches": 1.2, "Patates douces": 1.5, "Tomates pelées": 1, "Oignons": 0.2, "Ail": 0.03, "Gingembre": 0.05,
  "Mélange d'épices indien": 0.25, "Graines de moutarde jaune": 0.2, H: 0.04, "Riz": 0.4},
 "Tremper 2 kg de soja 12 h la veille (0,8 kg pour demain midi) et le cuire 2 h 30 à 3 h, en commençant tôt. Faire sauter les graines de moutarde dans l'huile, ajouter oignon, ail, gingembre et épices, puis les tomates, la patate douce en dés et un verre d'eau, 15 min. Ajouter 1,2 kg (poids sec) de soja cuit, 10 min. Réserver le reste au frais."),
(16, "din", "Poulet poêlé à l'ail et aux herbes, pommes de terre sautées, chou",
 {"Blanc de poulet": 0.9, "Pommes de terre": 2.0, "Ail": 0.04, "Herbes italiennes": 0.2, "Margarine": 0.08, "Chou blanc": 0.25,
  "Moutarde forte": 0.1, H: 0.06},
 "Précuire les pommes de terre en morceaux 10 min à la vapeur, puis les faire sauter dans l'huile 15 min jusqu'à ce qu'elles dorent. Saisir le poulet en morceaux avec l'ail et les herbes 8 min, finir avec la margarine et la moutarde. Faire poêler le chou 4 min."),
(17, "dej", "Soja et tempeh croustillants au sambal (façon kering), riz et chou sauté",
 {"Graines de soja sèches": 0.8, "Tempeh": 0.7, "Sambal": 0.02, "Sauce Bangkok (Kokita)": 0.1, "Ail": 0.03, "Oignons": 0.1, "Chou blanc": 0.25,
  H: 0.08, "Riz": 0.4},
 "Décongeler le tempeh la veille. Bien égoutter et sécher le soja cuit hier ; faire frire séparément le soja et le tempeh en petits dés, en 2 fois, 8 à 10 min jusqu'à ce qu'ils croustillent. Faire revenir ail et oignon, ajouter le sambal et la sauce Bangkok, enrober le soja. Chou sauté 4 min, riz."),
(17, "din", "Dahl de lentilles et courge aux graines de moutarde, riz",
 {"Lentilles en conserve": 4, "Lait de coco": 1, "Courge": 0.5, "Mélange d'épices indien": 0.25, "Graines de moutarde noire": 0.2,
  "Gingembre": 0.05, "Ail": 0.03, "Oignons": 0.2, H: 0.04, "Riz": 0.5},
 "Riz. Faire sauter les graines de moutarde dans l'huile, ajouter oignon, ail, gingembre et épices. Ajouter la courge en petits dés et un verre d'eau, 12 min, puis les lentilles égouttées et le lait de coco, 10 min. Écraser grossièrement."),
(18, "dej", "Salade de haricots blancs au thon, oignon et herbes",
 {"Haricots blancs secs": 0.8, "Thon": 3, "Oignons": 0.15, "Huile d'olive vierge extra": 0.06, "Herbes italiennes": 0.2,
  "Moutarde forte": 0.1},
 "Tremper les haricots la veille, les cuire 1 h le matin et les refroidir. Mélanger avec le thon et l'oignon émincé. Vinaigrette : huile, moutarde, herbes, sel, poivre."),
(18, "din", "Mie goreng au tempeh, œufs et légumes",
 {"Nouilles aux œufs (Atom Bulan)": 2, "Nouilles de riz": 1, "Tempeh": 0.7, "Œufs": 8, "Chou blanc": 0.25, "Oignons": 0.15, "Ail": 0.03,
  "Sauce Bangkok (Kokita)": 0.1, "Sambal": 0.02, H: 0.06},
 "Décongeler le tempeh la veille, le couper en dés et le dorer 6 min. Cuire les nouilles aux œufs 3 min, tremper les nouilles de riz 10 min, égoutter. Brouiller 4 œufs, réserver. Faire sauter ail, oignon et chou, ajouter les nouilles, la sauce Bangkok et le sambal, puis le tempeh et les œufs brouillés. Servir avec les 4 autres œufs au plat."),
(19, "dej", "Quinoa rouge et riz aux sardines et oignon",
 {"Quinoa rouge": 1, "Riz": 0.4, "Sardines (grande boîte)": 3, "Oignons": 0.1, "Huile d'olive vierge extra": 0.05},
 "Cuire ensemble le quinoa rincé et le riz dans 2 volumes d'eau, 15 min, laisser tiédir. Mélanger avec les sardines émiettées, l'oignon émincé, l'huile, du sel et du poivre."),
(19, "din", "Poulet coco-citronnelle et patate douce (lait de coco en poudre), riz",
 {"Blanc de poulet": 0.9, "Lait de coco en poudre": 1, "Patates douces": 1.5, "Citronnelle": 1, "Gingembre": 0.05, "Ail": 0.03,
  "Oignons": 0.15, "Sambal": 0.02, H: 0.04, "Riz": 0.5},
 "Délayer le sachet de lait de coco en poudre dans 1 L d'eau tiède. Faire revenir oignon, ail, gingembre et citronnelle écrasée, ajouter le poulet en cubes 5 min, puis la patate douce, le lait de coco et le sambal, 15 min. Servir avec le riz."),
(20, "dej", "Soupe épaisse de haricots rouges, courge et gingembre",
 {"Haricots rouges secs": 1.3, "Courge": 0.5, "Gingembre": 0.05, "Citronnelle": 1, "Oignons": 0.15, "Ail": 0.03,
  "Curry de Madras en poudre": 0.05, H: 0.03},
 "Tremper les haricots la veille et les cuire le matin (10 min à gros bouillons, puis 1 h à 1 h 30) : 1,3 kg pour une soupe qui tient au corps. Faire revenir oignon, ail, gingembre, citronnelle et curry, ajouter la courge en dés, les haricots et 3 L d'eau de cuisson, 20 min. Mixer à moitié pour épaissir, saler."),
(20, "din", "Curry de poulet aux pommes de terre, riz",
 {"Blanc de poulet": 0.9, "Pommes de terre": 0.8, "Curry de Madras en poudre": 0.1, "Oignons": 0.2,
  "Ail": 0.03, "Gingembre": 0.05, "Margarine": 0.05, H: 0.04, "Riz": 0.4},
 "Riz. Faire revenir oignon, ail et gingembre, ajouter le curry, puis le poulet en cubes 5 min. Ajouter les pommes de terre en dés et deux verres d'eau, mijoter 20 min. Finir avec la margarine."),
(21, "dej", "Salade tiède de soja, patate douce rôtie et sésame",
 {"Graines de soja sèches": 1.2, "Patates douces": 0.8, "Graines de sésame": 0.05, "Oignons": 0.1,
  "Huile d'olive vierge extra": 0.06},
 "Tremper 1,2 kg de soja 12 h la veille et le cuire 2 h 30 à 3 h dès le matin. Faire dorer la patate douce en cubes à la poêle 15 min. Mélanger avec le soja tiède, l'oignon émincé, l'huile, du sel et le sésame grillé."),
(21, "din", "Dîner d'arrivée : poulet grillé sambal-citron, riz au coco grillé, salade de chou",
 {"Blanc de poulet": 0.9, "Sambal": 0.03, "Citrons verts": 1, "Ail": 0.03, "Chou blanc": 0.25, "Copeaux de coco séchés": 0.3,
  H: 0.05, "Riz": 0.6},
 "Mariner le poulet en aiguillettes 30 min avec le sambal, l'ail et le jus du citron. Griller à la poêle très chaude 3 à 4 min par face. Griller les copeaux de coco à sec et les mélanger au riz chaud. Salade de chou émincé, huile et sel."),
]

# Limites de conservation estimées (dernier jour d'utilisation conseillé, chaleur humide, sans frigo sauf mention)
FRAIS = {"Tofu soyeux": 6, "Tomates fraîches": 5, "Concombres": 5, "Maïs (épis)": 5, "Haricots longs": 4,
         "Avocats": 12, "Yaourt nature": 14, "Mozzarella râpée": 14, "Carottes": 12, "Chayote": 18}
# Denrées entièrement consommables pendant les 21 jours (périssables ou faites pour ça)
PLEIN = set(FRAIS) | {"Chou blanc", "Courge", "Patates douces", "Pommes de terre", "Citronnelle", "Lait de coco en poudre",
                      "Vermicelles de soja (Longkou)", "Galettes de riz (feuilles)", "Olives vertes dénoyautées", "Câpres",
                      "Beurre cacahuète-amande", "Copeaux de coco séchés", "Mélange d'épices indien", "Graines de moutarde noire",
                      "Graines de moutarde jaune", "Nouilles aux œufs (Atom Bulan)", "Olives noires", "Herbes italiennes"}
RIZ_BORD = 12  # kg de riz à bord, saisis le 29/10
PART = 0.72  # part maximale des stocks durables consommée par les repas en 21 jours (21/30 + arrondis)

def check():
    errs, use, last = [], defaultdict(float), defaultdict(int)
    seen = set()
    for d, o, r, items, steps in M:
        if (d, o) in seen: errs.append(f"J{d} {o} en double")
        seen.add((d, o))
        for n, q in items.items():
            if n != H and n not in inv: errs.append(f"J{d} {o} : « {n} » absent de l'inventaire")
            use[n] += q; last[n] = max(last[n], d)
    if len(seen) != 42: errs.append(f"{len(seen)} repas au lieu de 42")
    # huile : tournesol d'abord, puis olive
    oil = use.pop(H)
    sun = min(oil, inv["Huile de cuisson"]["initial"] * 0.95)
    use["Huile de cuisson"] += sun; use["Huile d'olive vierge extra"] += oil - sun
    rows = []
    for n, q in sorted(use.items()):
        stock = RIZ_BORD if n == "Riz" else inv[n]["initial"]
        compte = not any(u in inv[n]["unit"] for u in ("kg", "L"))
        lim = stock if n in PLEIN else (round(stock * PART) if compte else stock * PART)
        if n in ("Huile de cuisson", "Huile d'olive vierge extra"): lim = stock
        if q > lim + 1e-9: errs.append(f"{n} : {q:g} {inv[n]['unit']} utilisés pour {stock:g} en stock (limite {lim:g})")
        if n in FRAIS and last[n] > FRAIS[n]: errs.append(f"{n} encore utilisé au J{last[n]} (limite J{FRAIS[n]})")
        rows.append((n, q, stock, inv[n]["unit"]))
    tom = use["Tomates concassées"] + use["Tomates pelées"]
    tom_stock = inv["Tomates concassées"]["initial"] + inv["Tomates pelées"]["initial"]
    if tom > round(tom_stock * PART): errs.append(f"tomates en boîte : {tom:g} pour {tom_stock:g}")
    oil_total = inv["Huile de cuisson"]["initial"] + inv["Huile d'olive vierge extra"]["initial"]
    if oil > oil_total * PART: errs.append(f"huile : {oil:.2f} L pour {oil_total:.2f} L")
    return errs, rows, use, oil

def build():
    errs, rows, use, oil = check()
    if errs: sys.exit("Menus refusés :\n- " + "\n- ".join(errs))
    menu = []
    for d in range(1, 22):
        day = {}
        for dd, o, r, items, steps in M:
            if dd != d: continue
            its = []
            oilq = items.get(H, 0)
            for n, q in items.items():
                if n == H: continue
                its.append([n, q])
            day["lunch" if o == "dej" else "dinner"] = {"recipe": r, "items": its, "oil": oilq, "steps": steps}
        menu.append(day)
    # huile : affectée au tournesol tant qu'il en reste, puis à l'olive (ordre chronologique)
    sun_left = inv["Huile de cuisson"]["initial"] * 0.95
    for day in menu:
        for k in ("lunch", "dinner"):
            m = day[k]; q = m.pop("oil")
            if not q: continue
            take = min(q, sun_left); sun_left -= take
            if take > 1e-9: m["items"].append(["Huile de cuisson", round(take, 3)])
            if q - take > 1e-9:
                for it in m["items"]:
                    if it[0] == "Huile d'olive vierge extra": it[1] = round(it[1] + q - take, 3); break
                else: m["items"].append(["Huile d'olive vierge extra", round(q - take, 3)])
    json.dump(menu, open(ICI / "menus-21j.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # lecture
    L = ["# Menus des 21 jours (8 personnes)", "",
         "Généré par `menus_21j.py` à partir de `inventaire.json`. Quantités pour 8, déjeuner et dîner. "
         "Petits-déjeuners, collations et fruits ne sont pas comptés.", ""]
    for i, day in enumerate(menu, 1):
        for k, lab in (("lunch", "Déjeuner"), ("dinner", "Dîner")):
            m = day[k]
            L += [f"## J{i} · {lab} : {m['recipe']}", "",
                  "Ingrédients : " + ", ".join(f"{n} {q:g} {inv[n]['unit']}" for n, q in m["items"]) + ".", "",
                  m["steps"], ""]
    L += ["## Bilan des stocks après 21 jours", "", "| Denrée | Repas | Stock | Reste | Unité |", "|---|---:|---:|---:|---|"]
    for n, q, s, u in rows:
        L.append(f"| {n} | {q:g} | {s:g} | {s - q:g} | {u} |")
    L += ["", f"Riz nécessaire : {use['Riz']:g} kg. Huile totale : {oil:.2f} L."]
    open(ICI / "menus-21j.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    return use, rows, oil

if __name__ == "__main__":
    use, rows, oil = build()
    print(f"42 repas validés. Riz nécessaire : {use['Riz']:g} kg ; huile : {oil:.2f} L.")
    for n, q, s, u in rows:
        print(f"  {n:40s} {q:7.2f} / {s:7.2f} {u}  ({q / s * 100 if s else 0:4.0f} %)")
