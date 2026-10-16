# AI Prompts

## Problem 1: Vibe Coder Prompts

### Original Prompt

```text
we are on homeowrk number 4 save things to that flder however i want u working based out of the root - i made a folder titled homework four- there is some data given to us for the assignment.  Create a virtual environment and do not read anything in the env file in the root. i updatd the key for the PORT_KEY_Api key cause i burned through the last.  All llm calls should use gpt6 luna.  I am going to work one problem at a time in this problem.  like the other homeworks.  i will tell you what problem we are on and you should annotate clearly in the prompt  and output file.  all followup prompts should be included.  word for word everytime.  the file name is asusual AI_prompts.md.  when you describe the problem number it should also contain a title.  thi is for problem 1.  titled Vibe coder prompts.  If i have a follow up prompt i will describe why i needed it for at least one of the follow ups - prompt me if i dont provide this before moving onto the next file. we are making a website for Campus Customs from the last assignment with a helpful chatbot.  we will be building a react + vite typescript front end and a python fastapi backend whose brain is pydanticAI agent.  Shoppers will be able to browse products and create an account , chat about merch, see matching items appear on the page, and get honest asnwers about price and stock from a local database.  u have the campus_customs.db with tables.  passwords are hashed.  The style will be yale themed that i will describe details (dont just assume).  do not make anything now until i prompt u  (other that the prompt file discussed above).  we will walk through all the steps.  in the end we will push the project to a public github repro.  do not commit the database or product images
```

### Follow-Up Prompt

```text
this is a follow up - u should be working in homework 4 folder.  there is no agent.md file yet.  create the virtual environemnt. use gpot-6.  why the follow up prompt was needed is because you starting working out the root due to a typo with what homework folder to work in..  never read the env file
```

### Why I Needed a Follow-Up Prompt

The agent started working out of the root folder because of a typo in my original prompt about which homework folder to work in.

## Problem 2: Analyze the Database

### Original Prompt

```text
we are on problem 2 titled analyze the database.  look at the campus_customs.db file make it so i can open it up and look at the fields.  make a output folder and place a harness.md file in there.  the harness should contain the tools i later decribe.  memory - chat history and current portfolio state.  stopping rules - llm should not burn through 0.1 of api calls in a single request.  guardrails - no inventing data, refuse unsafe asks that are illegal or try to gain access to any part of the website or get free stuff.  audit trail - we will keeo a trail of what the agent does (will be specified later). i will specify more rules once i can inspect the database.  ask me before procedding.  u should give me a link (html if you want) so i can look through it)
```

### Follow-Up Prompts

#### Follow-Up 1

```text
yes to 1 and2.  also the html link doesnt open up.  try again
```

**Why I needed it:** I needed the follow-up because the database viewer wasn't working.

#### Follow-Up 2

```text
for the harness file there are four tables in the database file.  there are different fields associated with each one.  write these down in the harness file.  also write one short line for why each field matters.  for example - product_id matters because it identifies a specific product.  also price matters because we want to know the cost for the user.  id is another important one - this is the user id who is specifically using the website.  the harness file should specifiy that these fields dont change .  passwords are protected using a has system.  this prompt was needed to complete the campus customes harness file after inspecting the database
```

**Why I needed it:** This prompt was needed to complete the Campus Customs harness file after inspecting the database.

## Problem 3: Build the Campus Customs Website

### Original Prompt

```text
we are on problem three titled build the campus customs website.  scaffold a react plus vite plus typescript front end for Campus customs.  make is blue and white yale themed.  having handsome dan be the mascot.  if you click him he goes back to the home page.  also periodically have him take out a bone and start chewing it.  he should be wearing a yale bandana.  there should be a navigation bar at the top that we can click to each section of the website.  Home, Products, About Us, Log in, Create account.  if there is a loading screen then have handsome dan walk across the screen while loading.look at yalebulldogblue.com for Home and About Us,  but my i have to put these pages in my own words ( do not copy the site text) . remeber I am creating the content on this.  The about us should state that a first year MBA student created the wesbite to provide a simple low cost way for student to get yale merch.  this is because there are high prices everywhere and th goal of this website is to not break the bank.  for the Home tab - we should have the popular items listedfirst no more than the top 5. the yale coat of arms should appear in a blue background at the top. on the products pafe, show product images from thecataolgue (use the image paths in the database) with basic infor (name, price description).  the prodcuts should have a filter to sort by mens womans, style of clothing, etc.  each page should show the top selling results for each category.  no more than 20.  then have page tabs to keep sifting through.  if you click the product a single item page should open (this will contain the image on the top left larger on the right show the description and the prices on the next line.  if its in stock make sure to indicate that in green bold font.  .clicking a card on the products page should take the shopper there.  there should be a small chat bubble option in the bottom right of the site ( a floating chat panel is fine).  does not need to talk to agent yet.  we will get that in the backend later.  i will need a small api soon to read the database.  it is fine to start a simple fast api app in backen/main.py just to serve procuts and images and then i will grow it into the agent in problem 5.
```

### Follow-Up Prompts

#### Follow-Up 1

```text
use an actual picture of handsome dan but make it slightly cartoony.  he also doesnt takeout the bone frequently and needs to be bigger. overall the site theme looks a little too Ai like.  I need more "apple like" design - keep it simple.  this is a follow up to problem three make sure it goes there in the file.  needed to make the frontend look better.
```

**Why I needed it:** Needed to make the frontend look better.

#### Follow-Up 2

```text
reason for the prompt was to confirm testing worked for accoutn login. back to problem 3. put my own image. make him slightly characterized.  still have the bone concept.  i dont like the tagline either. add a slight checkered (spaced out pattern - similiar to golf shirts in the background)  should be of the coat of arms - remeber tiny and not overpowering.  reason is to make front end better
```

**Why I needed it:** To make the front end better.

## Problem 4: Create Account and Log In

### Original Prompt

```text
on problem 4.  create a create account (firstname lastname, email, password (confirm pw too).  log in (email and pw).  new accounts go into the users table in the database.  passwords need to be stored securely with the hash so noone can hack them.  update harness for this too).  remeber all agents must adhere to the harness file.  we will test theseed database with the test user created already.  email is test@campuscustoms.yale.edu password is password and hash function PDKDF2-HMAC-SHA256, 120,00 ITERATIONS  stored as pbkdf2_sha256$salt$hash.  login checks a password by the following.  never unhas the stod value.  re-has what the use typed and compare.  read the salt out of the stored string (the middle piee) - do not make a new one at login.  hash the typed password with that same salt, then compare to the stored hash.  use a constant time compare.  singup and login must use the same hash settings (same function, same salt handling, same iteration count).  if they differ even the right pw will not match.  surest check. log in as the seeded test used and as a bran new account i will create in my app.  (i will do this).  update the harness with how auth works
```

### Follow-Up Prompts

#### Follow-Up 1

```text
testing in provlem 4 worked.
```

**Why I needed it:** The reason for the prompt was to confirm testing worked for account login.

## Problem 5: PydanticAI Agent Backend

### Original Prompt

```text
onto problem 5.  titled pydanticai agent backend. shop chatbot use fast api. plugged into front end chat widget.  put the api app in backend folder / main.py.  the is the file we will run with uvicorn.  keep the afgent as these four files next to it.  prompts/prompt.md system promp (we will grow this same file later), agent.py - agent entry/wiring.  tolls.py will be tools the agetn can call. models.py is the pydantic/pydanticai structured types.  in main.py expose a chat route so a messafe returns a reply from the agent.  use the portkey.  in the prompt.md use campus customes voice and safety basics - no cursing be professional, etc - the voice style should be like a bulldog but not annoying.  start or update types in models.py for chart replies procuct cards as needed.  in the harness note te the front end talks to fast api and the agent is loaded via prompt file + model.  bacnkend folder should run like this in termainal.uvicorn main:app --reload --port 8000
```

### Follow-Up Prompt

No follow-up prompt was used.

### Why I Needed a Follow-Up Prompt

No follow-up prompt was needed.

## Problem 6: Tools: Product Info and Stock

### Original Prompt

```text
onto problem 6 titeld tools: product info and stock.  now we are making tools - one for product description, price, how many are in stock (by size when customer asks) - agent should use the database to get this info.  dont invbent prioces or quantities.  make sure u indicate out of stock items with bold red text.  make sure the prompts/prompt.md so the agent knowsto call these tools for price and stock questions.  add or update return types in models.py.  in the harness fil u can now put the tools.  the fields i have chose are , id in inventory and the size and quantity to know if in stock. user id needed for past history and the email and name to address the user and to verify account with th email adress
```

### Follow-Up Prompt

No follow-up prompt was used.

### Why I Needed a Follow-Up Prompt

No follow-up prompt was needed.

## Problem 7: Chat Search That Updates the Page

### Original Prompt

```text
onto problem 7: chat search that updates the page.  if a customer asks about a type of item the agent should search the cat and the website should dunamically show those matching items as product cares (image, name, price, short info).  this is an api contract.  thje agent reutrns structured prodct matche and then the front end renders them on the website.  once its loaded dyannically, make sure the single item ape still works. update prompt.md and harness so it is clear how search results reach the page
```

### Follow-Up Prompt

No follow-up prompt was used.

### Why I Needed a Follow-Up Prompt

No follow-up prompt was needed.

## Problem 8: Customer Memory

### Original Prompt

```text
onto problem 8: customer memory.  when a shpper is logged in save their chat history in the database in the chat messages table and reload it when they return.  the agent should now who they chatting with as mentioned before (name and email.  put that into the agent deps and/ortolls the agent can call if not alreadt there.  put enough page context tht if someones on a pridcut page asnd asks a question the agent knows which product id they looking at.  put this feature into the agent contezt. also guest can chat but hostory only for users.  document in the harness how history is stored and what cuisotmer fields agent see and how page context is passed.
```

### Follow-Up Prompt

No follow-up prompt was used.

### Why I Needed a Follow-Up Prompt

No follow-up prompt was needed.

## Problem 9: Usability Improvements

### Original Prompt

```text
onto problem 9: usbaility improvements. for the front end - i want to add a coupon promo. so add a coupon tab. and upon coming the website have a popup that basically says if u register u get 10percent off.  so the two front end feratures are the pop up and then the tab if they exit out of the popuo.    if u register u get a promo code that takes off 10% of your order.  backend tool will need to be created to sent the code to display the code to the user upon loging in.  each user should get a unique code spe4cific to them tht only can be used once.  the backend tool should hae a generation fautre and then a prevent more than one use feature.  this should be tracked in the user database section. these are two backend tools.  also add a backend tool that loads up all the data upon first opening the apge.  that way loading should be really fast while clicking through the website..  also if the agent goes only more than three iterations of the same quesiton and the user gets frustratede instead of luna allow the model to temporarily increase in to sol for one request.  this is the "manager".  Putthese improvements in the out/usability.md before this is built.  make sure it specifies what i added and why it helps campus customs shopper or the busioness. afterwards i will test this and to see if it shows up in the running app.  add a section in it where u prompt me to type in my own words the results
```

### Follow-Up Prompts

#### Follow-Up 1

```text
when the code is applied sitewide should mark the price down by the amount with a strikethrough feature.  this was updated to meet the intent of theog request.  understand there is no cart for this assingment purposes
```

**Why I needed it:** This was updated to meet the intent of the original request.

#### Follow-Up 2

```text
for the test results - it needed an exact same prompt instead of a similiar one to get the manager to step in and the manager didnt really recommend a better product when i asked it to give me the best product.  the page is deifaintely fats. and the coupomn works for the pop up and the coupon tab.  the promo code generate feature worked and then prevented it from being used twice if u tried to apply it again. overall teh features seem to have worked. except for the slight hiccup with the manager.  add to the md file
```

**Why I needed it:** To record my test results for the usability improvements in output/usability.md.

#### Follow-Up 3

```text
ffix it and get rid of checklist in the usability .md and then also annotate in the md file it was fixed.
```

**Why I needed it:** To fix the manager hiccup found during testing and update usability.md.

#### Follow-Up 4

```text
get rid of the words after the manager fix - revert the words back to my own for the testing except for spelling errors.  for the manger retest it worked - not exact same words and the manager stepped in was actually a clairifcation with a slight gimmick to help out the customer.  update the usa file so my words like i talked about
```

**Why I needed it:** To keep my test results in my own words.

#### Follow-Up 5

```text
make sure it is clear what poriton of the file was built prior to or as i built it
```

**Why I needed it:** To make it clear which parts of usability.md were planned before building and which were added during the build.

## Problem 10: Style the Website

### Original Prompt

```text
onto problem 10: style the website.  i have already done a lot of styling as part of problem 3 so lets do more.  i will add another feature.  on the about us page ad the coat of arms faded background to the white portion and on the borders of the product page. add the cahgnes to the desing.md file, in the ouput.  also specificy in the files all the additions i did as part of problem 3.  in addition to the home page make a bottom banner with the a background of yale main campus buildings - like a skyline.  actially do this for every page.
```

### Follow-Up Prompts

#### Follow-Up 1

```text
the md file is too long and needs to be short and concrete per the homework requirements.  update as apporpiate
```

**Why I needed it:** The md file was too long and needed to be short and concrete per the homework requirements.

#### Follow-Up 2

```text
cant see the coat of arms on the webpage from the problem 10 additions. add a follow up pormpt why needed
```

**Why I needed it:** I couldn't see the coat of arms on the webpage from the Problem 10 additions.

#### Follow-Up 3

```text
nah get rid of the coat of arms - looks bad.  make them tiny and scttered like a golf shirt bu t very faded so its not overwhelming
```

**Why I needed it:** The large coat of arms looked bad, so I wanted tiny, scattered, very faded crests that aren't overwhelming.

#### Follow-Up 4

```text
dont see them
```

**Why I needed it:** I couldn't see the tiny crests on the page.

#### Follow-Up 5

```text
nah too much just ge rid of it.  add the crest to the thenbottom center of the page
```

**Why I needed it:** The scattered crests were too much, so I removed them and put one crest at the bottom center of the page.

#### Follow-Up 6

```text
make a note in the md file before i saw problem ten i was already styling it so the graders know why i inculdude it
```

**Why I needed it:** So the graders know why I included my Problem 3 styling in design.md.

## Problem 11: Site Testing (App Check)

### Original Prompt

```text
on problem 11: site testing (app check).  we are going to test the live siteand document it in output folder under appp_check.html ( a page i can double click open)  I need to include screenshots and short captions for the following (i will send screenshots and write captions - just reserve an area for them to be added) chatchecking the inventory level of an item (honest stock/price from the database 2. the dyanmic search result cards appearing after a category question (e.g. hoodies). 3. one of the usability geatures i added in problem 9 (for this one lets do the pop-up window). we want the html easy to grade - so a heading for each check, screenshot, one or two sentences i write what the ss proves.  put the screenshot files in output folderin app_check_images/ and link them from the app_check.html with the realtive paths (e.g app_check_images/inventory.png).  start building and i will send ss w captions here shortly.
```

### Follow-Up Prompts

#### Follow-Up 1

```text
this is the screenshot for my usability feature.  the shows that when you load the wbsite a promo code appears and ivites you to get it if you register.  the maybe later feature goes to the normal page but there is still a tab u can click if you want to get the coupon later
```

(Attached: screenshot of the register-for-10%-off popup, saved as `output/app_check_images/promo_popup.png`.)

**Why I needed it:** The follow-up prompts were needed to add the screenshots.

#### Follow-Up 2

```text
this is the dynamic model.  i asked for any quarterzips and this popped up with different types of quarterzips.  they are all quarterzips so the chat was accurate.  it also gives me the ability to clear the results if i want to go back to the homepage
```

(Attached: screenshot of the chat search result cards, saved as `output/app_check_images/search_cards.png`.)

**Why I needed it:** The follow-up prompts were needed to add the screenshots.

#### Follow-Up 3

```text
this is the inventory check - the chat got the question right of how many xl vintage bulldog hoodies they have.  this is confirmed by the detail page that lists 15 in stock.  it also annotes that xxl is out of stock in bold red font.
```

(Attached: screenshot of the chat inventory answer next to the item page, saved as `output/app_check_images/inventory.png`.)

**Why I needed it:** The follow-up prompts were needed to add the screenshots.

#### Follow-Up 4

```text
this completes question 11.  the follow up prompts were needed to add the screenshots
```

**Why I needed it:** To confirm Problem 11 is complete and give the reason for the follow-ups: they were needed to add the screenshots.

#### Follow-Up 5

```text
the screnshots are not showing.  please fix.  this follow up prompt was needed to fix the html.  send a link that i can open up in edge
```

**Why I needed it:** This follow-up prompt was needed to fix the HTML.

#### Follow-Up 6

```text
does the page double click to open?  needed to clarify
```

**Why I needed it:** Needed to clarify.

#### Follow-Up 7

```text
where is the website in the hw4 folder - added to clrify
```

**Why I needed it:** Added to clarify.

## Problem 12: Audit Trail, Safety, Finish Harness

### Original Prompt

```text
on problem 12: audit trail, safety, finish harness.  keep an append-only audit_trail.json in the output folder of agent loop acitvity (time, tool name, short args/result, stop reason).  do not wipe in between rns.  safety rules to be in the prompt folder under prompt.md.  the chat cannot use profanity or attempt to leave the website to research somehtin(no websearch).  for safety u cannot attempt to gather personal data about the customer or ask them for a credit card or other financila information. the chatbot should never reveal anything about other users or information about the inner workings of the website. we need to also finish the harness.md file so it is clear how the systme works.  model fields in models.py and why we chose them, tools and abilities, sfety rules, specs(loop limtis results, models, how to run front + back)
```

### Follow-Up Prompt

No follow-up prompt was used.

### Why I Needed a Follow-Up Prompt

No follow-up prompt was needed.

## Problem 13: Push to GitHub and Submit the URL

### Original Prompt

```text
onto problem 13 - we are going to make our code go into a folder titled hw4.  afterwards check to make sure everything works.  the file strucuture should be similiar but we added some additional databases for the promo code to work and other stiff.  we are going to push this to a public github repositiory.  walk me through how to get the repo link and set all that ip.  never put the real env file or the campus_customs.db or product images in the github repo.  use git.ignore and include env.exmaple w placeholders.  should be four agents and a readme
```

(Attached: screenshot of the Problem 13 instructions and expected file layout.)

### Follow-Up Prompts

#### Follow-Up 1

```text
it says to not put the campus_customs.db, or product images in the data folder in the githuib repo .  follow up because llm didnt listen
```

**Why I needed it:** Follow up because the LLM didn't listen.

#### Follow-Up 2

```text
need the promo db tho
```

**Why I needed it:** The promo code database needs to be in the repo.

#### Follow-Up 3

```text
how come i still see those two in the hw4 folder
```

**Why I needed it:** To understand why campus_customs.db and the product images are still in my hw4 folder.

#### Follow-Up 4

```text
push it
```

**Why I needed it:** To push the project to the public GitHub repo.
