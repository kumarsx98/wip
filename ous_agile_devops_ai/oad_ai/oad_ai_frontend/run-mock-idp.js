const express = require('express');
const bodyParser = require('body-parser');
const { ServiceProvider, IdentityProvider } = require('samlify');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

const baseUrl = 'https://mock-idp.example.com';

// Helper function to safely read files
function safeReadFile(filePath) {
  try {
    return fs.readFileSync(filePath, 'utf8');
  } catch (error) {
    console.error(`Error reading file ${filePath}:`, error.message);
    return null;
  }
}

// Read necessary files
const idpMetadata = safeReadFile(path.join(__dirname, 'idp_metadata.xml')); // Note the underscore
const idpKey = safeReadFile(path.join(__dirname, 'idp-key.pem'));
const idpCert = safeReadFile(path.join(__dirname, 'idp-cert.pem'));
const spMetadata = safeReadFile(path.join(__dirname, 'sp-metadata.xml'));

if (!idpMetadata || !idpKey || !idpCert || !spMetadata) {
  console.error('One or more required files are missing. Please check the file paths and try again.');
  process.exit(1);
}

// Create IdP
const idp = IdentityProvider({
  metadata: idpMetadata,
  privateKey: idpKey,
  cert: idpCert,
  isAssertionEncrypted: false,
});

// Create SP
const sp = ServiceProvider({
  metadata: spMetadata,
  assertionConsumerService: [
    {
      Binding: 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST',
      Location: 'http://localhost:8001/saml2/acs/',
    },
  ],
});

// SSO Endpoint
app.get('/saml2/sso/redirect', (req, res) => {
  const { SAMLRequest, RelayState } = req.query;
  const user = {
    email: 'user@example.com',
    firstName: 'Test',
    lastName: 'User',
  };

  idp.parseLoginRequest(sp, 'redirect', { query: req.query })
    .then(parseResult => {
      return idp.createLoginResponse(sp, parseResult, user, 'post', user.email);
    })
    .then(response => {
      res.render('samlresponse', {
        AcsUrl: sp.entityMeta.getAssertionConsumerService('post'),
        SAMLResponse: response.context,
        RelayState,
      });
    })
    .catch(err => {
      console.error(err);
      res.status(500).send('Internal Server Error');
    });
});

// Metadata Endpoint
app.get('/metadata', (req, res) => {
  res.header('Content-Type', 'text/xml').send(idp.getMetadata());
});

// Create a simple HTML template for rendering the SAML response
app.set('view engine', 'ejs');
app.set('views', __dirname);

// Add this EJS template in your project directory as 'samlresponse.ejs'
const ejsTemplate = `
<!DOCTYPE html>
<html>
<body>
    <form method="post" action="<%= AcsUrl %>">
        <input type="hidden" name="SAMLResponse" value="<%= SAMLResponse %>" />
        <% if (RelayState) { %>
        <input type="hidden" name="RelayState" value="<%= RelayState %>" />
        <% } %>
        <input type="submit" value="Submit" />
    </form>
    <script>
        document.forms[0].submit();
    </script>
</body>
</html>
`;

fs.writeFileSync(path.join(__dirname, 'samlresponse.ejs'), ejsTemplate);

// Start the server
const port = 7000;
app.listen(port, () => {
  console.log(`Mock IdP started on http://localhost:${port}`);
  console.log(`SSO entrypoint: http://localhost:${port}/saml2/sso/redirect`);
  console.log(`Metadata available at: http://localhost:${port}/metadata`);
});