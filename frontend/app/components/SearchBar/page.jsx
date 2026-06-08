"use client"
import React, { useState } from 'react';

const SearchBar = ({ currentQuery, setter }) => {

  const handleSearch = (e) => {
    setter(e.target.value);
  };
  return (
    <div>
      <input
        type="text"
        value={currentQuery}
        onChange={handleSearch}
        placeholder="Search..."
        className="px-2 py-1 border rounded"
      />
    </div>
  );
};

export default SearchBar;   