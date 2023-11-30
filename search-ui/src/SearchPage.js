import React from 'react';
import {
    SearchProvider,
    Results,
    SearchBox,
    Facet,
    Paging,
    PagingInfo
} from "@elastic/react-search-ui";
import './searchStyles.css';
import ElasticsearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";


// Retrieve username and password from environment variables
const username = process.env.REACT_APP_ELASTICSEARCH_USERNAME;
const password = process.env.REACT_APP_ELASTICSEARCH_PASSWORD;
const encodedCredentials = window.btoa(`${username}:${password}`);

// Retrieve host from environment variables
const host = process.env.REACT_APP_ELASTICSEARCH_HOST;

// Configure the connection to Elasticsearch
const connector = new ElasticsearchAPIConnector({
    host: host,
    index: "cv-transcriptions",
    connectionOptions: {
        headers: {
            Authorization: `Basic ${encodedCredentials}`
        }
    }
});

const configuration = {
    apiConnector: connector,
    searchQuery: {
        search_fields: {
            // Fields to search within
            generated_text: {}
        },
        result_fields: {
            // Fields to display in the results
            generated_text: { snippet: { size: 100, fallback: true } },
            duration: { raw: {} },
            age: { raw: {} },
            gender: { raw: {} },
            accent: { raw: {} }
        },
        facets: {
            // Define the fields you want to use as facets for filtering
            "age.keyword": { type: "value" },
            "gender.keyword": { type: "value" },
            "accent.keyword": { type: "value" }
        }
    },
    autocompleteQuery: {
        // Configuration for the search-as-you-type experience
        results: {
            result_fields: {
                generated_text: { snippet: { size: 100, fallback: true } }
            }
        }
    },
};

export default function SearchPage() {
    return (
        <SearchProvider config={configuration}>
            <div>
                <SearchBox />
                <PagingInfo />
                <Paging />
                <Facet field="age.keyword" label="Age" />
                <Facet field="gender.keyword" label="Gender" />
                <Facet field="accent.keyword" label="Accent" />
                <Results />
            </div>
        </SearchProvider>
    );
}


