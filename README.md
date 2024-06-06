Welkom bij de PICTURE-project repo. Dit is een repository over de stage van Simeon Hailemariam bij Active Collective. De repository bestaat uit:

- excel_label: Dit is een excel bestand waarin alle anatomische labels in staan.
- excel_label2: Dit is een excel bestand waarin labels staan die de labels in label.txt categoriseren.
- FN_masks map: Map met alle NIFTI False Negative regio's.
- talairach.nii: Dit is de atlas die gebruikt wordt voor het verkrijgen van de anatomische labels van de False Negative regio's.
- Segment.py: Generiek python bestand die door met de PICTURE Api te communiceren AI segmentaties verkrijgt.
- Compare.py: Generiek python bestand dat de respectievelijke AI segmentaties van PICTURE en expertsegmentaties van BraTS 2021 met elkaar vergelijkt.
- AAL_PICTURE.py: Generiek python bestand dat de FN maskers op de atlas mapt en anatomische labels verkrijgt en visualisaties doet hierover.

Gebruik:

Fork de originele vumc-picture-api repository en maak een nieuwe repository genaamd vumc-picture-api-stage.
Kloon de nieuwe geforkte repository naar je lokale machine met het commando:



Hernoem sample-secrets.env naar secrets.env.
Zet de NVIDIA GPU uit voor zowel registratie als segmentatie in docker-compose.yml.



Voeg een poort toe bij de api-sectie van docker-compose.yml voor communicatie met de API later.




Installeer handmatig proxy- en filteringnetwerken met de volgende Docker-opdrachten:

docker network create filtering
docker network create proxy.



Commentarieer SimpleITK in ./laravel/src/python_utils/requirements.txt en voeg een externe SimpleITK wheel toe aan de laravel directory. Voeg een COPY-commando toe aan de Dockerfile om het wielbestand te kopiëren: COPY SimpleITK-1.2.0-cp37-cp37m-manylinux1_x86_64.whl /tmp/





Bewerk de .env van Laravel zodat QUEUE_CONNECTION=redis wordt gewijzigd naar QUEUE_CONNECTION=sync.


Nu de containers bouwen met docker compose-up command.


Nu kan je met localhost:60/api verder


Nu is het taak om een gebruiker aan te maken, er zijn 2 manieren hoe je dit met behulp van php artisan tinker kunt doen:


Manier1:


Open terminal


Navigeer met cd vumc-picture-api-stage naar de repository


Ga in de api container zitten met command: docker exec -it vumc-picture-api-stage-api-1 /bin/sh (/bin/sh gebruik ik omdat ik linux gebruik)


Navigeer naar vumc-picture-api met cd var/www/laravel/vumc-picture-api


Doe nu het command: php artisan tinker


Nu ga je een gebruiker aanmaken met de volgende commands:


$user = new App\User;


$user->institute = ‘Vul hier de naam van je instituut in’;


$user->name = ‘Vul hier je naam in’;


$user->email = ‘Vul hier je e-mailadres’;


$user->email_verified_at = now();


$user->password = bcrypt(‘vul hier je wachtwoord’);


$user->super_user = true;


$user->active = true;


$user->activation_token = ‘token1’;


$user->save();


Uiteindelijk als de user goed is aangemaakt krijg je =true te zien


(optioneel) Zo kan je checken of je user goed aangemaakt is:
$user = App\User::where('email', '=', 'vul hier het e-mailadres')->first();


Dan ga je weer uit de api container met het command: exit


Manier2:


Open docker desktop


Ga naar de api container van de repository


Ga naar het tabblad exec


Navigeer naar vumc-picture-api met cd var/www/laravel/vumc-picture-api

Doe nu het command: php artisan tinker
Nu ga je een gebruiker aanmaken met de volgende commands:
$user = new App\User;
$user->institute = ‘Vul hier de naam van je instituut in’;
$user->name = ‘Vul hier je naam in’;
$user->email = ‘Vul hier je e-mailadres’;
$user->email_verified_at = now();
$user->password = bcrypt(‘vul hier je wachtwoord’);
$user->super_user = true;
$user->active = true;
$user->activation_token = ‘token1’;
$user->save();
Uiteindelijk als de user goed is aangemaakt krijg je =true te zien
(optioneel) Zo kan je checken of je user goed aangemaakt is:
$user = App\User::where('email', '=', 'vul hier het e-mailadres')->first();
Dan ga je weer uit de api container met het command: exit





Voorbereiding:
Voordat je kan beginnen met het segmenteren van bestanden moet eerst de dataset verkregen worden. In dit onderzoek wordt de BraTS2021 dataset gebruikt. Om de dataset te verkrijgen volg je deze stappen:
- Maak een account aan op www.Synpase.com
- Voer vervolgens het google formulier in om toegang te krijgen tot de dataset
- Je krijgt een mail met van de BraTS organisatie met de link naar de dataset, waar je die kan downloaden (het kan 1-3 werkdagen duren voordat je een mail terugkrijgt)
Segment.py:

Schrijf een generiek script in een gewenste IDE om te communiceren met de PICTURE API door het doen van requests volgens de volgende volgorde:

POST /user/login

Bij deze endpoint zijn parameters email en password verplicht.


POST /brain-maps/upload

Bij deze endpoint is parameter file verplicht.


PUT /brain-maps/upload-segmented/{uploadId}

Bij deze endpoint geef je metadata mee met de volgende parameters:




GET /brain-maps/upload

Geen parameters bij deze endpoint.


PUT /brain-maps/upload/{uploadId}

Bij deze endpoint geef je deze parameters mee:




GET /brain-map/{param}

Bij deze endpoint is parameter param verplicht. Tip: Gebruik brain map id voor param.


DELETE /brain-map/{param}

Bij deze endpoint is parameter param verplicht.





Compare.py:
Vergelijken van expert segmentaties met PICTURE segmentaties

Schrijf een generiek script die expert segmentaties met PICTURE segmentaties vergelijkt, de volgende stappen zitten daarin verwerkt:

Data Laden: De segmentaties gegenereerd door het PICTURE-model en de bijbehorende expert segmentaties worden ingeladen vanuit de respectievelijke bestanden.
Preprocessing: De dimensies van de PICTURE en expertsegmentaties komen niet overeen, zorg dat padding toegepast wordt om ervoor te zorgen dat ze dezelfde dimensies hebben.
Slice-analyse: Elke slice van het hersenvolume wordt afzonderlijk 1D geanalyseerd. Voor elke slice worden metrieken zoals de Dice-score, Jaccard-index, elementen van de Confusion Matrix berekend, accuracy, sensitivity en specificity berekend.
FN masks: Sla alle respectievelijke False Negative regio’s op voor de identificatie van de anatomische regio’s.
Visualisatie: Visualiseer elke slice voor een duidelijke visuele weergave die bijvoorbeeld: de T1 MRI-slice, de segmentatie van het PICTURE-model, de expert segmentatie en de gebieden van False Negatives toont.
Aggregatie en Statistieken: Bereken gemiddelde waarden voor de Dice-score, Jaccard-index en andere evaluatie metrieken over alle geanalyseerde slices per bestand. Bereken daarna opnieuw deze evaluatie metrieken, maar dan over het hele model.



AAL_PICTURE.py:
Identificeren van anatomische regio’s False Negatives met de talairach atlas
Voor de verbetering van het PICTURE model is het een idee om de locaties (anatomische regio’s) te detecteren die het model als false negative heeft geclassificeerd. Om dit te bereiken werd de Talairach atlas[13] gebruikt, een van de meest gebruikte atlassen in hersenonderzoek [14].


Plaats de labels van de Talairach atlas in een Excel-bestand, waarbij de voxelwaarden worden gekoppeld aan de respectievelijke anatomische labels. Wijs voxelwaarde 0 toe aan "No label" voor duidelijke visualisatie.


Maak een generiek script die de anatomische regio’s van de FN kan identificeren, de volgende stappen zitten daarin verwerkt:

De respectievelijke FN masks mapt op de talairach atlas
De voxelwaarden van de gemapte regio extraheert
De anatomische labels ophaalt.
Maak visualisaties om duidelijk een anatomisch beeld per FN-masker te krijgen. Bijvoorbeeld: cirkeldiagram met percentages voor elk anatomisch label.
