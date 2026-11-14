ASIM AI — UPDATED PUBLIC CHATBOT PROJECT

MODEL
Configured model ID is exactly gemini-3.7-flash. Google release notes say
requests to this deprecated ID are automatically routed by Google to
gemini-3.8-flash. This project does not change it to Gemini 2.5.

WHY FAILED TO FETCH APPEARS
GitHub Pages is static hosting and does not contain the /api/chat backend.
Deploy the frontend and backend together to Render and open the Render
onrender.com URL, NOT the github.io URL. The app now displays a clear message
if someone tries to chat from GitHub Pages.

DEPLOY
1. Replace/add index.html, app.py, requirements.txt and render.yaml in the
   ROOT of your GitHub repository.
2. In Render choose New > Blueprint and connect that GitHub repository.
3. Wait until the Render service status is Live.
4. In Render > Environment set GEMINI_API_KEY (secret), SUPABASE_ANON_KEY
   (your Supabase publishable/anon key), SUPABASE_URL (already in render.yaml),
   and GEMINI_MODEL=gemini-3.7-flash. Never put Gemini key in HTML/GitHub.
5. Deploy/redeploy. Open the Render service URL ending in onrender.com.
6. In Supabase > Authentication > URL Configuration add the Render URL to
   allowed Redirect URLs.

Security: never use the Supabase service_role key in the browser.
Render free services may sleep after inactivity and take time to wake.
