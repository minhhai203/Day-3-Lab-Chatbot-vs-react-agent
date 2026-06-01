__all__ = ["UniversityRegistrationChatbot"]

# Lazy import avoids the RuntimeWarning when running chatbot.py directly with -m,
# which causes the module to be loaded twice (once as the package, once as __main__).
def __getattr__(name):
    if name == "UniversityRegistrationChatbot":
        from .chatbot import UniversityRegistrationChatbot
        return UniversityRegistrationChatbot
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
