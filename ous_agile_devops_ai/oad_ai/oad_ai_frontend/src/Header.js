import React from 'react';

function Header({ djangoResult }) {
  return (
    <header>
      <img src={process.env.PUBLIC_URL + '/logo.jpg'} alt="Logo" className="logo" />
      {djangoResult}
    </header>
  );
}

export default Header;
