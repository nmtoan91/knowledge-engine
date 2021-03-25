package eu.interconnectproject.knowledge_engine.rest.api.client_example;

import java.io.IOException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import eu.interconnectproject.knowledge_engine.rest.model.CommunicativeAct;
import eu.interconnectproject.knowledge_engine.rest.model.HandleRequest;
import eu.interconnectproject.knowledge_engine.rest.model.HandleResponse;
import eu.interconnectproject.knowledge_engine.rest.model.SmartConnector;
import eu.interconnectproject.knowledge_engine.rest.model.Workaround;
import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class Client {
	private static final Logger LOG = LoggerFactory.getLogger(Client.class);

	public static final MediaType JSON = MediaType.get("application/json; charset=utf-8");
	private static final String SC = "/sc";
	private static final String KI = "/sc/ki";
	private static final String HANDLE = "/sc/handle";
	
	private OkHttpClient okClient;
	private final String baseUrl;
	private final ObjectMapper mapper = new ObjectMapper();
	private final Map<String, KnowledgeHandler> knowledgeHandlers = new HashMap<>();

	public Client(String aBaseUrl) {
		this.baseUrl = aBaseUrl;
		this.okClient = new OkHttpClient();
	}

	public void flushAll() {
		var scs = this.getScs();
		scs.forEach(sc -> {
			this.deleteSc(sc.getKnowledgeBaseId());
		});
	}

	public void postSc(String kbId, String kbName, String kbDesc) {
		var ilo = new SmartConnector().knowledgeBaseId(kbId).knowledgeBaseName(kbName).knowledgeBaseDescription(kbDesc);
		RequestBody body;
		try {
			body = RequestBody.create(mapper.writeValueAsString(ilo), JSON);
		} catch (JsonProcessingException e) {
			throw new RuntimeException("Could not serialize as JSON.");
		}
		Request request = new Request.Builder()
				.url(this.baseUrl + SC)
				.post(body)
				.build();
		try {
			this.okClient.newCall(request).execute();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	public List<SmartConnector> getScs() {
		Request request = new Request.Builder()
				.url(this.baseUrl + SC)
				.get()
				.build();
		Response response;
		try {
			response = this.okClient.newCall(request).execute();
			return this.mapper.readValue(response.body().string(), new TypeReference<List<SmartConnector>>(){});
		} catch (IOException e) {
			e.printStackTrace();
			throw new RuntimeException("Could not get SCs.");
		}
	}

	public void deleteSc(String kbId) {
		Request request = new Request.Builder()
				.url(this.baseUrl + SC)
				.delete()
				.header("Knowledge-Base-Id", kbId)
				.build();
		try {
			this.okClient.newCall(request).execute();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	private String postKi(String kbId, String type, String graphPattern, String argumentPattern, String resultPattern, List<String> requires, List<String> satisfies) {
		var workaround = new Workaround()
			.knowledgeInteractionType(type)
			.communicativeAct(new CommunicativeAct()
				.requiredPurposes(requires)
				.satisfiedPurposes(satisfies)
			)
			.graphPattern(graphPattern)
			.argumentGraphPattern(argumentPattern)
			.resultGraphPattern(resultPattern);
		RequestBody body;
		try {
			body = RequestBody.create(mapper.writeValueAsString(workaround), JSON);
		} catch (JsonProcessingException e) {
			throw new RuntimeException("Could not serialize as JSON.");
		}
		Request request = new Request.Builder()
				.url(this.baseUrl + KI)
				.post(body)
				.header("Knowledge-Base-Id", kbId)
				.build();
		try {
			var response = this.okClient.newCall(request).execute();
			return response.body().string();
		} catch (IOException e) {
			e.printStackTrace();
			throw new RuntimeException("Could not POST the new KI.");
		}
	}

	public String postKiAsk(String kbId, String graphPattern, List<String> requires, List<String> satisfies) {
		return this.postKi(kbId, "AskKnowledgeInteraction", graphPattern, null, null, requires, satisfies);
	}

	public String postKiAnswer(String kbId, String graphPattern, List<String> requires, List<String> satisfies, KnowledgeHandler handler) {
		this.knowledgeHandlers.put(kbId, handler);
		return this.postKi(kbId, "AnswerKnowledgeInteraction", graphPattern, null, null, requires, satisfies);
	}

	public String postKiPost(String kbId, String argumentPattern, String resultPattern, List<String> requires, List<String> satisfies) {
		return this.postKi(kbId, "PostKnowledgeInteraction", null, argumentPattern, resultPattern, requires, satisfies);
	}

	public String postKiReact(String kbId, String argumentPattern, String resultPattern, List<String> requires, List<String> satisfies, KnowledgeHandler handler) {
		this.knowledgeHandlers.put(kbId, handler);
		return this.postKi(kbId, "ReactKnowledgeInteraction", null, argumentPattern, resultPattern, requires, satisfies);
	}

	public void startLongPoll(String kbId) {
		Request request = new Request.Builder()
			.url(this.baseUrl + HANDLE)
			.get()
			.header("Knowledge-Base-Id", kbId)
			.build();

		// Do the request asynchronously, and schedule a callback.
		this.okClient.newCall(request).enqueue(new Callback() {
			@Override
			public void onFailure(Call call, IOException e) {
				LOG.error("Something went wrong during a handle call. Not repolling.", e);
			}

			@Override
			public void onResponse(Call call, Response response) throws IOException {
				if (response.code() ==  202) {
					LOG.info("Received 202 from GET /sc/handle. Repolling.");
					// Do another call to wait for a new task.
					startLongPoll(kbId);
				} else if (response.code() == 200) {
					LOG.info("Received 200 from GET /sc/handle. Sending response and then repolling.");
					
					HandleRequest handleRequest = mapper.readValue(response.body().string(), new TypeReference<HandleRequest>(){});
					String kiId = handleRequest.getKnowledgeInteractionId();
					var handler = knowledgeHandlers.get(kiId);
					var handleResult = handler.handle(handleRequest);
					postKnowledgeResponse(kbId, handleResult);
					startLongPoll(kbId);
				}
			}
		});
	}

	public void postKnowledgeResponse(String kbId, HandleResponse handleResult) {
		RequestBody body;
		try {
			body = RequestBody.create(mapper.writeValueAsString(handleResult), JSON);
		} catch (JsonProcessingException e) {
			throw new RuntimeException("Could not serialize as JSON.");
		}
		Request request = new Request.Builder()
				.url(this.baseUrl + HANDLE)
				.post(body)
				.header("Knowledge-Base-Id", kbId)
				.build();
		try {
			this.okClient.newCall(request).execute();
		} catch (IOException e) {
			e.printStackTrace();
			throw new RuntimeException("Could not POST the knowledge response.");
		}
	}

	public static void main(String[] args) throws IOException {
		var client = new Client("http://localhost:8080/rest");
		
		// First remove all existing smart connectors (a bit nuclear, but it does
		// the trick)
		client.flushAll();

		// Post a new SC with a POST KI.
		client.postSc("https://www.interconnectproject.eu/knowledge-engine/knowledgebase/example/a-kb", "A knowledge base", "A very descriptive piece of text.");
		String ki1 = client.postKiPost("https://www.interconnectproject.eu/knowledge-engine/knowledgebase/example/a-kb",
			"?a ?b ?c.",
			"?d ?e ?f.",
			Arrays.asList("https://www.tno.nl/energy/ontology/interconnect#InformPurpose"),
			Arrays.asList("https://www.tno.nl/energy/ontology/interconnect#InformPurpose")
		);
		LOG.info("Made new KI with ID {}", ki1);

		// Post another SC with a REACT KI.
		client.postSc("https://www.interconnectproject.eu/knowledge-engine/knowledgebase/example/another-kb", "Another knowledge base", "Another very descriptive piece of text.");
		String ki2 = client.postKiReact("https://www.interconnectproject.eu/knowledge-engine/knowledgebase/example/another-kb",
			"?a ?b ?c.",
			"?d ?e ?f.",
			Arrays.asList("https://www.tno.nl/energy/ontology/interconnect#InformPurpose"),
			Arrays.asList("https://www.tno.nl/energy/ontology/interconnect#InformPurpose"),
			new KnowledgeHandler() {
				@Override
				public HandleResponse handle(HandleRequest handleRequest) {
					// TODO Auto-generated method stub
					return null;
				}
			}
		);

		LOG.info("Made new KI with ID {}", ki2);
	}
}
