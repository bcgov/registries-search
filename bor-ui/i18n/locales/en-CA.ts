/* eslint-disable max-len */
export default {
  /* All sections should be in alphabetical order unless otherwise specified */
  connect: {
    header: {
      title: 'BC Registry and Online Services'
    }
  },
  docAccess: {
    BUSINESS_SUMMARY_FILING_HISTORY: 'Business Summary',
    CERTIFICATE_OF_GOOD_STANDING: 'Certificate of Good Standing',
    CERTIFICATE_OF_STATUS: 'Certificate of Status',
    LETTER_UNDER_SEAL: 'Letter Under Seal'
  },
  label: {
    actingInConcert: 'Acting in concert',
    actingJointly: 'Acting jointly',
    actions: 'Actions',
    beneficialOwner: 'Beneficial Owner',
    benefitCompanies: 'Benefit Companies',
    bcregDash: 'BC Registries Dashboard',
    born: 'Born',
    businessInformation: 'Business Information',
    businessName: 'Business Name',
    businessType: 'Business Type',
    businessNum: 'Business Number',
    businessPersonSearch: 'Business and Person Search',
    businessSummary: 'Business Summary',
    certStatus: 'Certificate of Status',
    certGoodStanding: 'Certificate of Good Standing',
    change: 'Change',
    controlShares: 'Control of Shares',
    controlVotes: 'Control of Votes',
    cooperativeAssociationsActive: 'Cooperative Associations (active only)',
    craBN: 'CRA Business Number',
    date: 'Date',
    dateTime: 'Date/Time',
    details: 'Details',
    directControl: 'Direct Control',
    directorControl: 'Control of Directors',
    directors: 'Directors',
    documentType: 'Document Type',
    documents: 'Documents',
    email: 'Email',
    filingHistoryDocsLedger: 'Filing History Documents (ledger filings)',
    findBusinessPerson: 'Find a business or person',
    from: 'From',
    generalPartnerships: 'General Partnerships',
    helpWithBPS: 'Help with Business and Person Search',
    hideHelp: 'Hide Help',
    incorpRegNum: 'Incorporation/ Registration Number',
    incorporationNum: 'Incorporation Number',
    indirectControl: 'Indirect Control',
    letterUnderSeal: 'Letter Under Seal',
    myBusReg: 'My Business Registry',
    multiple: 'Multiple',
    nA: 'Not Available',
    number: 'Number',
    ok: 'OK',
    oneSelected: '1 Selected',
    other: 'Other',
    paid: 'Paid',
    paymentPending: 'Payment Pending',
    paymentFailed: 'Payment Failed',
    phone: 'Phone',
    preferredName: 'Preferred Name',
    purchasedDate: 'Purchased Date/Time (pacific time)',
    purchasedItems: 'Purchased Items',
    registeredOwner: 'Registered Owner',
    registrationNum: 'Registration Number',
    search: 'Search',
    searchBusinesses: 'Search Businesses',
    searchDirectors: 'Search Directors',
    searchPeople: 'Search People',
    searchResults: 'Search Results',
    shares: 'Shares',
    significantIndividuals: 'Significant Individuals',
    significantInfluence: 'Significant Influence',
    soleProprietorships: 'Sole Proprietorships',
    status: 'Status',
    tryAgain: 'Try Again',
    unknownCompany: 'Unknown Company',
    userName: 'User Name',
    viewDocuments: 'View Documents',
    viewPurchasedDocuments: 'View documents',
    votes: 'Votes'
  },
  legalType: {
    BC: 'BC Limited Company',
    BEN: 'BC Benefit Company',
    CP: 'BC Cooperative Association',
    GP: 'BC General Partnership',
    SP: 'BC Sole Proprietorship',
    undefined: 'N/A'
  },
  search: {
    business: {
      extended: {
        error: 'Enter a business name or number',
        hint: "Example: 'Test Construction Inc.', 'BC0000123', '987654321BC0001'",
        info: 'Search for businesses registered or incorporated in B.C. and access their business documents.',
        placeholder: 'Business Name or Incorporation/Registration Number or CRA Business Number'
      },
      limited: {
        error: 'Enter a business name or number',
        hint: "Example: 'Test Construction Inc.', 'BC0000123', '987654321BC0001'",
        info: 'Search for businesses registered or incorporated in B.C. and access their business documents.',
        placeholder: 'Business Name or Incorporation/Registration Number or CRA Business Number'
      },
      public: {
        error: 'Enter a business name or number',
        hint: "Example: 'Test Construction Inc.', 'BC0000123', '987654321BC0001'",
        info: 'Search for businesses registered or incorporated in B.C. and access their business documents.',
        placeholder: 'Business Name or Incorporation/Registration Number or CRA Business Number'
      }
    },
    person: {
      extended: {
        error: 'Enter a name, address, SIN/TTN/ITN, and/or email address',
        help1: 'The person search returns results for people associated with businesses registered in British Columbia.',
        help2: "You can find people by searching for any part of the person's name, preferred name, address, email, or SIN. Note that all searches prioritize name matches, so searches for an address will list name matches first. For example, searches for Parker Ave. will list matches for peoples' names containing Parker above addresses containing Parker.",
        hint: "Example: 'John Smith', '123 Main St', 'V1V 1V1', 'John Smith Victoria', 'j.smith{'@'}123.aba', '000 000 000'",
        info: 'Search for the names, addresses, SIN/TTN/ITN, and email addresses of people associated with businesses in B.C.',
        placeholder: 'Person Name, Address, SIN/TTN/ITN, and/or Email Address'
      },
      limited: {
        error: 'Enter a name',
        help1: 'The person search returns results for partners and proprietors associated with businesses registered in British Columbia.',
        help2: "You can find people by searching for any part of the person's name or address, or their business email address. Note that all searches prioritize name matches, so searches for an address will list name matches first. For example, searches for Parker Ave. will list matches for peoples' names containing Parker above addresses containing Parker.",
        hint: "Example: 'John Smith'",
        info: 'Search for the names of partners and proprietors associated with businesses in B.C.',
        placeholder: 'Person Name'
      },
      public: {
        error: 'Enter a name',
        help1: 'The person search returns results for partners and proprietors associated with businesses registered in British Columbia.',
        help2: "You can find people by searching for any part of the person's name.",
        hint: "Example: 'John Smith'",
        info: 'Search for the names of partners and proprietors associated with businesses in B.C.',
        placeholder: 'Person Name'
      }
    },
    director: {
      extended: {
        error: 'Enter a name, address, and/or business email address',
        hint: "Example: 'John Smith', '123 Main St', 'V1V 1V1', 'John Smith Victoria', 'j.corp{'@'}123.aba'",
        info: 'Search for the names, addresses, and business email addresses of people associated with businesses in B.C.',
        placeholder: 'Person Name, Address, and/or Business Email Address'
      },
      limited: {
        error: 'Enter a name, address, and/or business email address',
        hint: "Example: 'John Smith', '123 Main St', 'V1V 1V1', 'John Smith Victoria', 'j.corp{'@'}123.aba'",
        info: 'Search for the names, addresses, and business email addresses of people associated with businesses in B.C.',
        placeholder: 'Person Name, Address, and/or Business Email Address'
      }
    }
  },
  status: {
    active: 'Active',
    historical: 'Historical'
  },
  text: {
    accessBusinesstooltip: "You can access this business through BC OnLine or by contacting BC Registries. See 'Help with Business and Person Search' for details.",
    control: {
      percentage: 'At least {min}% and up to {max}%',
      icon: {
        beneficialOwner: 'Beneficial owner (e.g., through a trust)',
        beneficialOwnerDisplay: 'Beneficial owner of shares or votes',
        directControl: 'Direct control',
        directControlDisplay: 'Direct control of directors',
        indirectControl: 'Indirect control of shares or votes',
        indirectControlDir: 'Indirect control of directors',
        indirectControlDisplay: 'Indirect control (e.g., through another business)',
        other: 'Any other reason(s) this individual is a significant individual',
        registeredOwner: 'Registered owner',
        registeredOwnerDisplay: 'Registered owner of shares or votes',
        significantInfluence: 'Significant influence of directors',
        significantInfluenceDisplay: 'Significant influence control'
      }
    },
    dialog: {
      error: {
        contact: 'If this issue persists, please contact us.',
        default: 'The Business Dashboard application is currently unavailable. Please try again later.',
        download: 'File cannot be downloaded due to an application error. Please try again later.'
      }
    },
    errorRetry: 'We were unable to retrieve your recent purchases. Please try again later.',
    errorRetrySearch: 'We are unable to display your search results. Please try again later.',
    exportedSearchResults: 'Search results successfully exported in the order displayed in the table.',
    noPurchases: 'No purchases in the last 14 days',
    noSI: 'Company indicated no significant individuals',
    notEntered: '(Not entered)',
    saveAsAbove: 'saveAsAbove',
    tableInfo: 'This table will display up to 1000 of the most recent document activity in the last 14 days.',
    viewBusinessInformationHelp: 'You can directly view information for the business types listed below in Business and Person Search. Information for other business types can be obtained through ',
    whereAvailDocsInclude: 'Where available, documents for these business types include:'
  }
}
