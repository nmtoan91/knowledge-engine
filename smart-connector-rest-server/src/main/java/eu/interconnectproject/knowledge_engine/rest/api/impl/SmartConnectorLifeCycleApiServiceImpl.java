package eu.interconnectproject.knowledge_engine.rest.api.impl;

import java.net.URI;
import java.net.URISyntaxException;
import java.util.HashSet;
import java.util.Set;

import javax.ws.rs.core.Context;
import javax.ws.rs.core.Response;
import javax.ws.rs.core.SecurityContext;
import javax.ws.rs.*;
import javax.ws.rs.container.*;
import javax.validation.constraints.*;
import javax.validation.Valid;

import io.swagger.annotations.ApiParam;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import eu.interconnectproject.knowledge_engine.rest.model.SmartConnector;
import eu.interconnectproject.knowledge_engine.rest.api.NotFoundException;

@Path("/sc")
public class SmartConnectorLifeCycleApiServiceImpl {

	private static final Logger LOG = LoggerFactory.getLogger(SmartConnectorLifeCycleApiServiceImpl.class);

	private RestKnowledgeBaseManager manager = RestKnowledgeBaseManager.newInstance();

	@GET
	@Produces({ "application/json; charset=UTF-8", "text/plain; charset=UTF-8" })
	@io.swagger.annotations.ApiOperation(value = "Either get all available Smart Connectors or a specific one if the Knowledge-Base-Id is provided.", notes = "", response = SmartConnector.class, responseContainer = "List", tags={ "smart connector life cycle", })
	@io.swagger.annotations.ApiResponses(value = {
		@io.swagger.annotations.ApiResponse(code = 200, message = "A list of Smart Connectors. It will have only a single element if the Knowledge-Base-Id was provided.", response = SmartConnector.class, responseContainer = "List"),
		@io.swagger.annotations.ApiResponse(code = 404, message = "If there is no Smart Connector for the given Knowledge-Base-Id.", response = String.class),
		@io.swagger.annotations.ApiResponse(code = 500, message = "If a problem occurred.", response = String.class)
	})
	public void scGet(
		@ApiParam(value = "The knowledge base id who's Smart Connector information you would like to have." )@HeaderParam("Knowledge-Base-Id") String knowledgeBaseId,
		@Suspended final AsyncResponse asyncResponse,
		@Context SecurityContext securityContext
	) throws NotFoundException {
		LOG.debug("scGet called: {}", knowledgeBaseId);

		if (knowledgeBaseId == null) {
			asyncResponse.resume(Response.ok().entity(convertToModel(this.manager.getKBs())).build());
			return;
		} else {
			try {
				new URI(knowledgeBaseId);
			} catch (URISyntaxException e) {
				asyncResponse.resume(Response.status(400).entity("Knowledge base not found, because its ID must be a valid URI.")
						.build());
				return;
			}
			if (this.manager.hasKB(knowledgeBaseId)) {
				Set<RestKnowledgeBase> connectors = new HashSet<>();
				connectors.add(this.manager.getKB(knowledgeBaseId));
				asyncResponse.resume(Response.ok().entity(convertToModel(connectors)).build());
				return;
			} else {
				asyncResponse.resume(Response.status(404).entity("Knowledge base not found.").build());
				return;
			}
		}
	}

	@POST	
	@Consumes({ "application/json; charset=UTF-8" })
	@Produces({ "text/plain; charset=UTF-8" })
	@io.swagger.annotations.ApiOperation(value = "Create a new Smart Connector for the given Knowledge Base.", notes = "", response = Void.class, tags={ "smart connector life cycle", })
	@io.swagger.annotations.ApiResponses(value = {
		@io.swagger.annotations.ApiResponse(code = 200, message = "If the Smart Connector for the given Knowledge Base is successfully created.", response = Void.class),
		@io.swagger.annotations.ApiResponse(code = 400, message = "If the creation of the Smart Connector for the given Knowledge Base failed.", response = String.class)
	})
	public void scPost(
		@ApiParam(value = "", required = true) @NotNull @Valid  SmartConnector smartConnector,
		@Suspended final AsyncResponse asyncResponse,
		@Context SecurityContext securityContext
	) throws NotFoundException {
		if (smartConnector.getKnowledgeBaseId().isEmpty()) {
			asyncResponse.resume(Response.status(400).entity("Knowledge Base ID must be a non-empty URI.").build());
			return;
		}

		URI kbId;
		try {
			kbId = new URI(smartConnector.getKnowledgeBaseId());
		} catch (URISyntaxException e) {
			asyncResponse.resume(Response.status(400).entity("Knowledge base ID must be a valid URI.").build());
			return;
		}

		final String kbDescription = smartConnector.getKnowledgeBaseDescription();
		final String kbName = smartConnector.getKnowledgeBaseName();

		if (this.manager.hasKB(smartConnector.getKnowledgeBaseId())) {
			asyncResponse.resume(Response.status(400).entity("That knowledge base ID is already in use.").build());
			return;
		}

		// Tell the manager to create a KB, store it, and have it set up a SC etc.
		this.manager.createKB(new SmartConnector().knowledgeBaseId(kbId.toString()).knowledgeBaseName(kbName)
			.knowledgeBaseDescription(kbDescription)).thenRun(() -> {
				LOG.info("Returning response for smart connector with ID {}", kbId);
				asyncResponse.resume(Response.ok().build());
			});

		LOG.info("Creating smart connector with ID {}.", kbId);

		return;
	}

	@DELETE
	@Produces({ "text/plain; charset=UTF-8" })
	@io.swagger.annotations.ApiOperation(value = "Delete the Smart Connector belonging to the given Knowledge Base", notes = "", response = Void.class, tags={ "smart connector life cycle", })
	@io.swagger.annotations.ApiResponses(value = {
		@io.swagger.annotations.ApiResponse(code = 200, message = "If the Smart Connector for the given Knowledge Base is successfully deleted.", response = Void.class),
		@io.swagger.annotations.ApiResponse(code = 404, message = "If there is no Smart Connector for the given Knowledge-Base-Id.", response = String.class)
	})
	public void scDelete(
		@ApiParam(value = "The knowledge base id who's smart connector should be deleted." ,required=true)@HeaderParam("Knowledge-Base-Id") String knowledgeBaseId,
		@Suspended final AsyncResponse asyncResponse,
		@Context SecurityContext securityContext
	) throws NotFoundException {
		LOG.info("scDelete called: {}", knowledgeBaseId);

		if (knowledgeBaseId == null) {
			asyncResponse.resume(Response.status(Response.Status.BAD_REQUEST).entity("Knowledge-Base-Id header should not be null.").build());
			return;
		}

		try {
			new URI(knowledgeBaseId);
		} catch (URISyntaxException e) {
			asyncResponse.resume(Response.status(400).entity("Knowledge base not found, because its ID must be a valid URI.").build());
			return;
		}

		if (manager.hasKB(knowledgeBaseId)) {
			manager.deleteKB(knowledgeBaseId);
		} else {
			asyncResponse.resume(Response.status(404).entity("Deletion of knowledge base failed, because it could not be found.")
					.build());
			return;
		}
		asyncResponse.resume(Response.ok().build());
		return;
	}

	private eu.interconnectproject.knowledge_engine.rest.model.SmartConnector[] convertToModel(
			Set<RestKnowledgeBase> kbs) {
		return kbs.stream().map((restKb) -> {
			return new eu.interconnectproject.knowledge_engine.rest.model.SmartConnector()
					.knowledgeBaseId(restKb.getKnowledgeBaseId().toString())
					.knowledgeBaseName(restKb.getKnowledgeBaseName())
					.knowledgeBaseDescription(restKb.getKnowledgeBaseDescription());
		}).toArray(eu.interconnectproject.knowledge_engine.rest.model.SmartConnector[]::new);
	}
}
