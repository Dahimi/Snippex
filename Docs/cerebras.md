> ## Documentation Index
> Fetch the complete documentation index at: https://inference-docs.cerebras.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Structured Outputs

> Generate structured data with the Cerebras Inference API

<Tip>
  [**To get started with a free API key, click here.**](https://cloud.cerebras.ai?utm_source=inferencedocs)
</Tip>

Structured outputs is a feature that can enforce consistent JSON outputs for models in the Cerebras Inference API. This is particularly useful when building applications that need to process AI-generated data programmatically. Some of the key benefits of using structured outputs are:

* **Reduced Variability**: Ensures consistent outputs by adhering to predefined fields.
* **Type Safety**: Enforces correct data types, preventing mismatches.
* **Easier Parsing & Integration**: Enables direct use in applications without extra processing.

## Tutorial: Structured Outputs using Cerebras Inference

In this tutorial, we'll explore how to use structured outputs with the Cerebras Cloud SDK. We'll build a simple application that generates movie recommendations and uses structured outputs to ensure the response is in a consistent JSON format.

<Steps>
  <Step title="Initial Setup">
    First, ensure that you have completed steps 1 and 2 of our [Quickstart Guide](/quickstart) to set up your API key and install the Cerebras Cloud SDK.

    Then, initialize the Cerebras client and import the necessary modules we will use in this tutorial.

    <CodeGroup>
      ```python Python theme={null}
      import os
      from cerebras.cloud.sdk import Cerebras
      import json

      client = Cerebras(
          api_key=os.environ.get("CEREBRAS_API_KEY")
      )
      ```

      ```javascript Node.js theme={null}
      import Cerebras from '@cerebras/cerebras_cloud_sdk';

      const client = new Cerebras({
        apiKey: process.env['CEREBRAS_API_KEY']
      });
      ```
    </CodeGroup>
  </Step>

  <Step title="Defining the Schema">
    To ensure structured responses from the model, we'll use a JSON schema to define our output structure. Start by defining your schema, which specifies the fields, their types, and which ones are required. For our example, we'll define a schema for a movie recommendation that includes the title, director, and year:

    <Warning>
      Note: For every `required` array you define in your schema, you must set `additionalProperties` to `false`.
    </Warning>

    <CodeGroup>
      ```python Python theme={null}
      movie_schema = {
          "type": "object",
          "properties": {
              "title": {"type": "string"},
              "director": {"type": "string"},
              "year": {"type": "integer"},
          },
          "required": ["title", "director", "year"],
          "additionalProperties": False
      }
      ```

      ```javascript Node.js theme={null}
      const movieSchema = {
          type: "object",
          properties: {
              title: { type: "string" },
              director: { type: "string" }, 
              year: { type: "integer" },
          },
          required: ["title", "director", "year"],
          additionalProperties: false
      };
      ```
    </CodeGroup>
  </Step>

  <Step title="Using Structured Outputs">
    Next, use the schema in your API call by setting the `response_format` parameter to include both the type and your schema. Setting `strict` to `true` will enforce the schema. Setting `strict` to `false` will allow the model to return additional fields that are not specified in the schema, similar to [JSON mode](#json-mode).

    <CodeGroup>
      ```python Python theme={null}
      completion = client.chat.completions.create(
          model="gpt-oss-120b",
          messages=[
              {"role": "system", "content": "You are a helpful assistant that generates movie recommendations."},
              {"role": "user", "content": "Suggest a sci-fi movie from the 1990s"}
          ],
          response_format={
              "type": "json_schema", 
              "json_schema": {
                  "name": "movie_schema",
                  "strict": True,
                  "schema": movie_schema
              }
          }
      )

      # Parse the JSON response
      movie_data = json.loads(completion.choices[0].message.content)
      print(json.dumps(movie_data, indent=2))
      ```

      ```javascript Node.js theme={null}
      async function main() {
        const schemaCompletion = await client.chat.completions.create({
          model: 'gpt-oss-120b',
          messages: [
            { role: 'system', content: 'You are a helpful assistant that generates movie recommendations.' },
            { role: 'user', content: 'Suggest a sci-fi movie from the 1990s' }
          ],
          response_format: {
            type: 'json_schema', 
            json_schema: {
              name: 'movie_schema',
              strict: true,
              schema: movieSchema
            }
          }
        });
        
        // Parse and display the JSON response 
        const schemaMovieData = JSON.parse(schemaCompletion.choices[0].message.content);
        console.log('Movie Recommendation:');
        console.log(JSON.stringify(schemaMovieData, null, 2));
      }
      ```
    </CodeGroup>

    Sample output:

    ```
    {
      "title": "Terminator 2: Judgment Day",
      "director": "James Cameron",
      "year": 1991
    }
    ```

    Now you have a structured JSON response from the model, which can be used in your application.
  </Step>
</Steps>

## Understanding Strict Mode

Strict mode guarantees that the model's output will exactly match the JSON schema you provide. When `strict` is set to `true`, Cerebras employs constrained decoding to ensure schema conformance at the token level, making invalid outputs impossible.

### Why Use Strict Mode

Without strict mode, you may encounter:

* Malformed JSON that fails to parse
* Missing required fields
* Incorrect data types (e.g., `"16"` instead of `16`)
* Extra fields not defined in your schema

With strict model enabled, you get:

* *Guaranteed* valid JSON
* Schema compliance: Every field matches your specification
* Type safety: Correct data types for all properties
* No retries needed: Eliminates error handling for schema violations

### Enabling Strict Mode

Set `strict` to `true` in your `response_format` configuration:

```python  theme={null}
response_format={
    "type": "json_schema",
    "json_schema": {
        "name": "my_schema",
        "strict": True,  # Enable constrained decoding
        "schema": your_schema
    }
}
```

### Schema Requirements for Strict Mode

When using strict mode, you must set `additionalProperties: false`. This is required for every object in your schema.

### Limitations in Strict Mode

When strict mode is enabled, your schema must conform to specific requirements. See the [Supported Schemas](#supported-schemas) section for detailed information on constraints, limits, and unsupported features.

## Schema References and Definitions

You can use `$ref` with `$defs` to define reusable schema components within your JSON schema. This is useful for avoiding repetition and creating more maintainable schemas.

```python highlight={5,7-8} theme={null}
schema_with_defs = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "director": {"$ref": "#/$defs/person"},
        "year": {"type": "integer"},
        "lead_actor": {"$ref": "#/$defs/person"},
        "studio": {"$ref": "#/$defs/studio"}
    },
    "required": ["title", "director", "year"],
    "additionalProperties": False,
    "$defs": {
        "person": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name"],
            "additionalProperties": False
        },
        "studio": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "founded": {"type": "integer"},
                "headquarters": {"type": "string"}
            },
            "required": ["name"],
            "additionalProperties": False
        }
    }
}
```

## Supported Schemas

Structured Outputs supports a subset of [JSON Schema](https://json-schema.org/docs). This section outlines the supported types, properties, and constraints.

### Supported Types

The following types are supported for Structured Outputs:

| Type      | Description                       |
| --------- | --------------------------------- |
| `string`  | Text values                       |
| `number`  | Numeric values (floating point)   |
| `integer` | Whole number values               |
| `boolean` | True/false values                 |
| `object`  | Nested objects with properties    |
| `array`   | Lists of items                    |
| `enum`    | Constrained set of allowed values |
| `null`    | Null values                       |
| `anyOf`   | Union types                       |

### Schema Constraints

When using strict mode, the following constraints apply:

| Constraint                | Limit                                           |
| ------------------------- | ----------------------------------------------- |
| Maximum schema length     | 5,000 characters                                |
| Maximum nesting depth     | 10 levels                                       |
| Maximum object properties | 500                                             |
| Maximum total enum values | 500 across all enum properties                  |
| Single enum string length | 7,500 characters (when > 250 total enum values) |

### Required Schema Structure

All schemas must follow these rules:

* **Root must be an object**: The top-level schema must have `"type": "object"`.
* **No additional properties**: You must set `"additionalProperties": false` for every object in your schema.

<Note>
  Schemas that do not follow these rules may be allowed in some cases today. Starting **July 21, 2026**, these requirements will be strictly enforced for all models and non-conforming schemas will return a validation error. To ensure forward compatibility, always follow these rules in your schema definitions. For more information about API versioning and deprecation timelines, see [API Versions](/api-reference/versions).
</Note>

### Supported Features

Your schema can include the following JSON Schema features:

* **Nested structures**: Define complex objects with nested properties.
* **Required fields**: Specify which fields must be present.
* **Enums (value constraints)**: Use the `enum` keyword to whitelist the exact literals a field may take. See `rating` in the example below.
* **Schema references**: Use `$ref` with `$defs` to define reusable schema components within your schema.
* **Tuple validation**: `items: false` is supported when used with `prefixItems` for tuple-like arrays.
* **Number constraints**: Use `minimum`, `maximum`, `exclusiveMinimum`, `exclusiveMaximum`, and `multipleOf` to constrain `number` and `integer` values.

### Unsupported Features

The following JSON Schema features are **not** supported in strict mode:

| Feature              | Notes                                                                            |
| -------------------- | -------------------------------------------------------------------------------- |
| Recursive schemas    | Self-referencing schemas are not supported                                       |
| External `$ref`      | References to external URLs are blocked for security                             |
| `$anchor` keyword    | Use relative paths within definitions instead                                    |
| `items: true`        | Not supported for array types                                                    |
| Informational fields | Additional fields meant as guidelines (not used in validation) are not supported |
| String `pattern`     | Regular expression constraints on strings are not supported                      |
| String `format`      | Format validation (e.g., `email`, `date-time`, `uuid`) is not supported          |
| Array constraints    | `minItems`, `maxItems` are not supported                                         |

### Example: Complex Schema

For example, a more complex schema might look like:

```python  theme={null}
detailed_schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "director": {"type": "string"},
        "year": {"type": "integer"},
        "genres": {
            "type": "array",
            "items": {"type": "string"}
        },
        "rating": {
            "type": "string",
            "enum": ["G", "PG", "PG‑13", "R"]
        },
        "cast": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "role": {"type": "string"}
                },
                "required": ["name"],
                "additionalProperties": False
            }
        }
    },
    "required": ["title", "director", "year", "genres"],
    "additionalProperties": False
}
```

When used with the API, you might get a response like:

```json  theme={null}
{
  "title": "Jurassic Park",
  "director": "Steven Spielberg",
  "year": 1993,
  "genres": ["Science Fiction", "Adventure", "Thriller"],
  "cast": [
    {"name": "Sam Neill", "role": "Dr. Alan Grant"},
    {"name": "Laura Dern", "role": "Dr. Ellie Sattler"},
    {"name": "Jeff Goldblum", "role": "Dr. Ian Malcolm"}
  ]
}
```

### Key Ordering

The keys in the generated JSON output will appear in the same order as they are defined in your schema.

## Working with Pydantic and Zod

Besides defining a JSON schema manually, you can use Pydantic (Python) or Zod (JavaScript) to create your schema and convert it to JSON. Pydantic's `model_json_schema` and Zod's `zodToJsonSchema` methods generate the JSON schema, which can then be used in the API call, as demonstrated in the workflow above.

<CodeGroup>
  ```python Python (Pydantic) theme={null}
  from pydantic import BaseModel
  import json

  # Define your schema using Pydantic
  class Movie(BaseModel):
      title: str
      director: str 
      year: int 

  # Convert the Pydantic model to a JSON schema
  movie_schema = Movie.model_json_schema()

  # Print the JSON schema to verify it
  print(json.dumps(movie_schema, indent=2))
  ```

  ```javascript Node.js (Zod) theme={null}
  import { z } from 'zod';
  import { zodToJsonSchema } from 'zod-to-json-schema';

  // Define your schema using Zod
  const MovieSchema = z.object({
    title: z.string(),
    director: z.string(),
    year: z.number().int()
  });

  // Convert the Zod schema to a JSON schema
  const movieJsonSchema = zodToJsonSchema(MovieSchema, { name: 'movie_schema' });

  // Print the JSON schema to verify it
  console.log(JSON.stringify(movieJsonSchema, null, 2));
  ```
</CodeGroup>

## JSON Mode

JSON mode is an alternative to structured outputs that generates JSON responses without enforcing a specific schema. The model decides what fields to include based on the context of your prompt.

<Note>
  We recommend using structured outputs with `strict` set to `true` instead of JSON mode whenever possible. Structured outputs guarantee schema adherence, while JSON mode only ensures valid JSON without enforcing a specific structure.
</Note>

To use JSON mode, set the `response_format` parameter to `json_object` and include instructions in your message asking the model to respond in JSON format:

<CodeGroup>
  ```python Python theme={null}
  completion = client.chat.completions.create(
      model="gpt-oss-120b",
      messages=[
        {"role": "system", "content": "You are a helpful assistant that generates movie recommendations. Respond with JSON."},
        {"role": "user", "content": "Suggest a sci-fi movie from the 1990s"}
      ],
      response_format={"type": "json_object"}
  )
  ```

  ```javascript Node.js theme={null}
  async function main() {
    const jsonModeCompletion = await client.chat.completions.create({
      model: 'gpt-oss-120b',
      messages: [
        { role: 'system', content: 'You are a helpful assistant that generates movie recommendations. Respond with JSON.' },
        { role: 'user', content: 'Suggest a sci-fi movie from the 1990s' }
      ],
      response_format: {
        type: 'json_object'
      }
    });
  }
  ```
</CodeGroup>

### Structured Outputs vs JSON Mode

The table below summarizes the key differences between Structured Outputs and JSON Mode:

| Feature              | Structured Outputs                                                                         | JSON Mode                                  |
| -------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------ |
| Outputs valid JSON   | Yes                                                                                        | Yes                                        |
| Enforces schema      | Yes (when `strict: true`)                                                                  | No                                         |
| Constrained decoding | Yes (when `strict: true`)                                                                  | No                                         |
| Configuration        | `response_format: { type: "json_schema", json_schema: { "strict": true, "schema": ... } }` | `response_format: { type: "json_object" }` |

<Warning>
  `tools` and `response_format` cannot be used in the same request.
</Warning>

## Conclusion

Structured outputs with JSON schema enforcement ensures your AI-generated responses follow a consistent, predictable format. This makes it easier to build reliable applications that can process AI outputs programmatically without worrying about unexpected data structures or missing fields.

Check out some of our other tutorials to learn more about other features of the Cerebras Inference SDK:

* [Tool Use](/capabilities/tool-use): extending models' capabilities to access tools to answer questions and perform actions
* [Streaming](/capabilities/streaming): a feature for streaming responses from the model
* [CePO](/capabilities/cepo): a reasoning framework for improving reasoning model abilities with test-time compute
