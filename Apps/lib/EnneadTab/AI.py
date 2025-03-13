import time
import EXE
import SECRET
import DATA_FILE
import UI

def translate(input_text, 
              target_language="cn", 
              personality="professional architect, precise, concise, and creative"):
    """Translates input text to target language using an external translation service.
    
    Args:
        input_text: Text to be translated
        target_language: Target language code (default: "cn")
        personality: Translation style guidance for AI translator
        
    Returns:
        Translated text or error message if translation fails
    """
    api = SECRET.get_api_key("EnneadTabAPI")
    if not api:
        return ""
    data = {"input_text":input_text, 
            "target_language":target_language, 
            "personality":personality,
            "api_key":api}
    DATA_FILE.set_data(data, "translator_input.sexyDuck")
    EXE.try_open_app("Translator.exe")

    max_wait = 900
    
    def check_status(iter):
        status = DATA_FILE.get_data("translator_input.sexyDuck").get("status")
        if status == "done":
            # Signal progress bar to complete immediately
            return True

        time.sleep(0.1)
        return False

    # Progress bar will terminate early when check_status returns True
    UI.progress_bar(list(range(max_wait)), 
                   func=check_status, 
                   label_func=lambda x: "Translating...{}/{}s".format(x/10, int(max_wait/10)))  # Assuming this parameter exists
    
    # Check final status outside the progress bar
    wait = 500
    while wait > 0:
        status = DATA_FILE.get_data("translator_input.sexyDuck").get("status")
        if status == "done":
            result = DATA_FILE.get_data("translator_output.sexyDuck")
            return result["output_text"]
        time.sleep(0.1)
        wait -= 1
    print ("Translation failed")
    return ""



def translate_multiple(input_texts, 
              target_language="cn", 
              personality="professional architect, precise, concise, and creative, \
                  i will give you a list of item to translate, \
                  please translate them all in the same style and tone, \
                  you will return a list of translated words only, no marker formating, \
                  if the input contain both English and Chinese, \
                  please just focus on translating the English part and ignore Chinese part"):

    input = "\n".join([str(x).strip() for x in input_texts if len(str(x).strip()) != 0])

    
    result = translate(input, target_language, personality)
    if not result or result == "":  # If translation is empty
        return {}  # Return original texts
        
    result_list = result.split("\n")
    # Ensure we have enough translations by padding with original texts if needed
    while len(result_list) < len(input_texts):
        result_list.append("")
        
    return {k: v.strip() or k for k, v in zip(input_texts, result_list)}


if __name__ == "__main__":
    sample_sentences = ["The sun is shining brightly today", "I love to play soccer with my friends", "The cat is sleeping on the couch", 
                        "The book is on the top shelf", "The baby is laughing at the clown", "The flowers are blooming in the garden", 
                        "The dog is barking loudly outside", "The kids are playing in the park", "The teacher is writing on the board", 
                        "The phone is ringing on the table", "The music is playing in the background", "The cake is delicious and moist", 
                        "The car is driving down the street", "The bike is leaning against the wall", "The tree is swaying in the wind", 
                        "The bird is singing a sweet melody", "The fish is swimming in the ocean", "The computer is turning on slowly", 
                        "The door is opening with a creak", "The window is shining with the morning light", "The mirror is reflecting my smile", 
                        "The pencil is rolling off the desk", "The paper is flying through the air", "The chair is creaking with age", 
                        "The table is wobbling on its legs", "The lamp is shining brightly in the corner", "The clock is ticking away", 
                        "The calendar is hanging on the wall", "The picture is framed and beautiful", "The vase is filled with fresh flowers", 
                        "The bookshelf is overflowing with books", "The rug is soft and plush under my feet", "The curtains are blowing in the breeze", 
                        "The fan is spinning lazily above", "The heater is warming up the room", "The air conditioner is cooling us down", 
                        "The refrigerator is humming in the kitchen", "The stove is cooking up a storm", "The sink is filled with dirty dishes", 
                        "The toilet is flushing with a roar", "The shower is pouring down warm water", "The bathtub is filled with bubbles", 
                        "The soap is slippery in my hands", "The shampoo is cleaning my hair", "The towel is drying me off", 
                        "The bed is comfortable and cozy", "The pillow is soft and fluffy", "The blanket is warm and snug", 
                        "The alarm clock is ringing loudly", "The radio is playing music in the background", "The television is showing a movie", 
                        "The phone is ringing with an incoming call", "The doorbell is ringing with a visitor", "The mailman is delivering the mail", 
                        "The newspaper is filled with current events", "The magazine is filled with interesting articles", "The catalog is filled with products", 
                        "The brochure is filled with information", "The flyer is advertising a sale", "The poster is hanging on the wall", 
                        "The banner is streaming across the screen", "The logo is representing the company", "The trademark is protecting the brand", 
                        "The copyright is protecting the work", "The patent is protecting the invention", "The license is allowing use", 
                        "The contract is binding the agreement", "The agreement is mutually beneficial", "The partnership is working together", 
                        "The team is collaborating on the project", "The group is discussing the topic", "The meeting is being held in the conference room", 
                        "The presentation is being given by the CEO", "The speech is being delivered by the president", "The lecture is being taught by the professor", 
                        "The lesson is being learned by the student", "The test is being taken by the class", "The exam is being graded by the teacher", 
                        "The grade is being given to the student", "The report is being written by the journalist", "The article is being published in the newspaper", 
                        "The book is being written by the author", "The story is being told by the narrator", "The poem is being recited by the poet", 
                        "The song is being sung by the singer", "The music is being played by the orchestra", "The dance is being performed by the dancers", 
                        "The play is being acted out by the actors", "The movie is being shown on the screen", "The video is being recorded by the camera", 
                        "The photo is being taken by the photographer", "The picture is being painted by the artist", "The sculpture is being created by the sculptor", 
                        "The building is being constructed by the architect", "The bridge is being built by the engineer", "The road is being paved by the construction worker", 
                        "The car is being driven by the driver", "The bike is being ridden by the cyclist", "The train is being operated by the conductor", 
                        "The plane is being flown by the pilot", "The boat is being sailed by the sailor", "The ship is being captained by the captain", 
                        "The submarine is being commanded by the commander", "The spacecraft is being controlled by the astronaut", "The rocket is being launched by the engineer", 
                        "The satellite is being orbited by the satellite", "The planet is being explored by the astronaut", "The star is being studied by the astronomer", 
                        "The galaxy is being observed by the telescope", "The universe is being understood by the scientist", "The theory is being proven by the experiment", 
                        "The law is being enforced by the police", "The rule is being followed by the citizen", "The regulation is being obeyed by the business", 
                        "The policy is being implemented by the government", "The decision is being made by the leader", "The choice is being selected by the voter", 
                        "The vote is being counted by the election official", "The result is being announced by the news anchor", "The winner is being congratulated by the crowd", 
                        "The loser is being comforted by the friend", "The tie is being broken by the referee", "The game is being played by the players", 
                        "The sport is being enjoyed by the fans", "The hobby is being pursued by the enthusiast", "The interest is being explored by the curious", 
                        "The passion is being ignited by the spark", "The fire is being fueled by the flame", "The flame is being extinguished by the fire extinguisher", 
                        "The smoke is being cleared by the fan", "The air is being purified by the filter", "The water is being cleaned by the purification system", 
                        "The earth is being protected by the conservationist", "The environment is being preserved by the activist", "The wildlife is being protected by the ranger", 
                        "The forest is being maintained by the forester", "The park is being managed by the park ranger", "The garden is being tended by the gardener", 
                        "The farm is being worked by the farmer", "The field is being cultivated by the agricultural worker", "The crop is being harvested by the farmer", 
                        "The fruit is being picked by the fruit picker", "The vegetable is being planted by the gardener", "The flower is being watered by the florist", 
                        "The tree is being pruned by the arborist", "The branch is being trimmed by the pruner", "The leaf is being raked by the landscaper", 
                        "The grass is being mowed by the lawn mower", "The lawn is being maintained by the groundskeeper", "The yard is being cleaned by the janitor", 
                        "The house is being built by the contractor", "The building is being constructed by the construction worker", "The apartment is being rented by the tenant", 
                        "The room is being decorated by the interior designer", "The furniture is being arranged by the furniture mover", "The carpet is being installed by the carpet installer", 
                        "The floor is being polished by the janitor", "The wall is being painted by the painter", "The ceiling is being repaired by the repairman", 
                        "The roof is being replaced by the roofer", "The window is being cleaned by the window cleaner", "The door is being installed by the carpenter", 
                        "The lock is being fixed by the locksmith", "The key is being made by the key maker", "The alarm is being installed by the security expert", 
                        "The camera is being monitored by the security guard", "The sensor is being triggered by the motion detector", "The light is being turned on by the switch", 
                        "The electricity is being generated by the power plant", "The energy is being conserved by the conservationist", "The water is being heated by the heater", 
                        "The gas is being pumped by the pump", "The oil is being drilled by the oil rig", "The coal is being mined by the miner", "The mineral is being extracted by the miner", 
                        "The metal is being forged by the blacksmith", "The steel is being produced by the steel mill", "The aluminum is being recycled by the recycler", 
                        "The plastic is being molded by the mold maker", "The glass is being blown by the glassblower", "The ceramic is being fired by the potter", 
                        "The wood is being carved by the woodcarver", "The stone is being sculpted by the sculptor", "The fabric is being woven by the weaver", 
                        "The thread is being sewn by the seamstress", "The yarn is being knitted by the knitter", "The rope is being tied by the sailor", 
                        "The net is being cast by the fisherman", "The hook is being baited by the angler", "The line is being cast by the fisherman", 
                        "The fish is being caught by the fisherman", "The bird is being caught by the bird hunter", "The rabbit is being hunted by the hunter", 
                        "The deer is being hunted by the hunter", "The bear is being hunted by the hunter", "The wolf is being hunted by the hunter", 
                        "The fox is being hunted by the hunter", "The rabbit is being hunted by the hunter", "The deer is being hunted by the hunter", 
                        "The bear is being hunted by the hunter", "The wolf is being hunted by the hunter", "The fox is being hunted by the hunter", 
                        "The rabbit is being hunted by the hunter", "The deer is being hunted by the hunter", "The bear is being hunted by the hunter", 
                        "The wolf is being hunted by the hunter", "The fox is being hunted by the hunter", "The rabbit is being hunted by the hunter"]
    print (translate_multiple(sample_sentences))

    


