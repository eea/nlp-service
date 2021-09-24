The ES base query looks like (and is modified for):

        {
           "query":{
              "function_score":{
                 "query":{
                    "bool":{
                       # "must":[
                       #    {
                       #       "multi_match":{
                       #          "query":"water",
                       #          "fields":[
                       #             "title^2",
                       #             "subject^1.5",
                       #             "description^1.5",
                       #             "searchable_spatial^1.2",
                       #             "searchable_places^1.2",
                       #             "searchable_objectProvides^1.4",
                       #             "searchable_topics^1.2",
                       #             "searchable_time_coverage^10",
                       #             "searchable_organisation^2",
                       #             "label",
                       #             "all_fields_for_freetext"
                       #          ]
                       #       }
                       #    }
                       # ],
                       "filter":[
                          {
                             "bool":{
                                "should":[
                                   {
                                      "term":{
                                         "language":"en"
                                      }
                                   }
                                ],
                                "minimum_should_match":1
                             }
                          },
                          {
                             "bool":{
                                "should":[
                                   {
                                      "range":{
                                         "readingTime":{}
                                      }
                                   }
                                ],
                                "minimum_should_match":1
                             }
                          },
                          {
                             "term":{
                                "hasWorkflowState":"published"
                             }
                          },
                          {
                             "constant_score":{
                                "filter":{
                                   "bool":{
                                      "should":[
                                         {
                                            "bool":{
                                               "must_not":{
                                                  "exists":{
                                                     "field":"issued"
                                                  }
                                               }
                                            }
                                         },
                                         {
                                            "range":{
                                               "issued.date":{
                                                  "lte":"2021-09-24T11:47:45Z"
                                               }
                                            }
                                         }
                                      ]
                                   }
                                }
                             }
                          },
                          {
                             "constant_score":{
                                "filter":{
                                   "bool":{
                                      "should":[
                                         {
                                            "bool":{
                                               "must_not":{
                                                  "exists":{
                                                     "field":"expires"
                                                  }
                                               }
                                            }
                                         },
                                         {
                                            "range":{
                                               "expires":{
                                                  "gte":"2021-09-24T09:26:33Z"
                                               }
                                            }
                                         }
                                      ]
                                   }
                                }
                             }
                          }
                       ]
                    }
                 },
                 "functions":[
                    {
                        "script_score": {
                            "query": {"match_all": {}},
                            "script": {
                                # offset score to ensure a positive range as required by Elasticsearch
                                "source": f"{similarity_fn_name}(params.query_vector,'{self.embedding_field}') + 1000",
                                "params": {"query_vector": query_emb.tolist()},
                            },
                        }
                    }

                    {
                       "exp":{
                          "issued.date":{
                             "offset":"30d",
                             "scale":"1800d"
                          }
                       }
                    },
                    {
                       "script_score":{
                          "script":"doc['items_count_references'].value*0.01"
                       }
                    },

                 ],
                 "score_mode":"sum"
              }
           },
           "highlight":{
              "fragment_size":200,
              "number_of_fragments":1,
              "fields":{

              }
           },
           "aggs":{

           },
           "size":20,
           "track_total_hits":true
        }

