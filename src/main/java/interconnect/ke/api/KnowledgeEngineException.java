package interconnect.ke.api;

/**
 * A Knowledge Engine specific exception that can be used to wrap multiple other
 * exceptions.
 */
public class KnowledgeEngineException extends Exception {

	private static final long serialVersionUID = 1L;

	public KnowledgeEngineException(Throwable t) {
		super(t);
	}

}
